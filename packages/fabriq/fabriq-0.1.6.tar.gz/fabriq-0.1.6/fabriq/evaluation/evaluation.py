from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    GEval,
    FaithfulnessMetric,
    HallucinationMetric,
    SummarizationMetric,
)
from deepeval.test_case import LLMTestCase
from deepeval.models.base_model import DeepEvalBaseLLM
from fabriq.llm_model import LLMModel
import traceback

class _CustomModel(DeepEvalBaseLLM):
    def __init__(self, config):
        self.config = config
        self.model = LLMModel(config).llm_model

    def load_model(self):
        return self.model

    def generate(self, prompt: str):
        resp = self.model.invoke(prompt).content
        return resp

    async def a_generate(self, prompt: str):
        resp = await self.model.ainvoke(prompt)
        return resp.content

    def get_model_name(self):
        return self.model.name


class Evaluation:
    def __init__(self, config):
        self.config = config
        self.model = _CustomModel(config)

    def run_evaluation(self, test_cases: list[LLMTestCase], metrics: list[str]):
        results = evaluate(test_cases=test_cases, metrics=metrics)
        return results

    def get_metrics(self):
        return [
            AnswerRelevancyMetric(),
            ContextualPrecisionMetric(),
            ContextualRecallMetric(),
            ContextualRelevancyMetric(),
            GEval(),
            FaithfulnessMetric(),
            HallucinationMetric(),
            SummarizationMetric(),
        ]

    def rag_evaluation(
        self,
        retrieved_docs: list[str],
        query: str = None,
        answer: str = None,
        expected_answer: str = None,
    ):
        metrics = [
            ContextualPrecisionMetric(model=self.model),
            ContextualRecallMetric(model=self.model),
            ContextualRelevancyMetric(model=self.model),
            HallucinationMetric(model=self.model),
        ]
        test_case = LLMTestCase(
            input=query,
            actual_output=answer,
            expected_output=expected_answer,
            retrieval_context=retrieved_docs,
            context=retrieved_docs,
        )

        results = {}
        for metric in metrics:
            try:
                metric_result = evaluate(test_cases=[test_case], metrics=[metric])
                results[metric.__class__.__name__] = {
                    "Score": metric_result.test_results[0].metrics_data[0].score,
                    "Reason": metric_result.test_results[0].metrics_data[0].reason,
                }
            except Exception as e:
                results[metric.__class__.__name__] = (
                    f"Skipped (insufficient parameters): {e}"
                )
                print(traceback.format_exc())
        return results
