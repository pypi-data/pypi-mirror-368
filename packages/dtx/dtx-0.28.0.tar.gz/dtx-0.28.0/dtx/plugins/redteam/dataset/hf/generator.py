from typing import Iterator, List

from dtx_models.analysis import (
    PromptDataset,
    RiskItem,
)
from dtx_models.prompts import MultiTurnTestPrompt, MultiturnTestPrompts
from dtx.plugins.redteam.dataset.hf.adapters.base import MultiTurnConversation
from dtx.plugins.redteam.dataset.hf.hf_prompts_repo import HFPromptsGenerator

# ----------------------
# LangChain-based Test Prompt Generator
# ----------------------


class HFDataset_PromptsGenerator:
    """
    Generates test prompts and evaluation criteria for each attack strategy.
    """

    def __init__(self, hf_prompts_gen: HFPromptsGenerator):
        """
        Initializes the OpenAI model.

        hf_datasets: List of HF datasets
        """
        self._generator = hf_prompts_gen

    def generate(
        self,
        dataset: PromptDataset,
        app_name: str,
        threat_desc: str,
        risks: List[RiskItem],
        max_prompts: int = 10,
        max_prompts_per_plugin: int = 5,
        max_goals_per_plugin: int = 5
    ) -> Iterator[MultiturnTestPrompts]:
        """
        Generates test prompts and evaluation criteria for attack strategies of each risk,
        with a limit on the total number of generated prompts.
        :param dataset PromptDataset: dataset to fetch the prompts from
        :param app_name: Name of the AI application
        :param threat_desc: Summary of security risks/threats related to the app
        :param risks: List of RiskItem objects
        :param max_prompts: Maximum number of test prompts to generate
        :param max_prompts_per_plugin: Maximum number of test prompts to generate per risk
        :return: Iterator of RiskItem objects containing generated test prompts and evaluation criteria
        """
        total_prompts = 0
        _prompt_gen = self._generator.get_generator(dataset=dataset)
        for risk in risks:
            total_prompts_per_risk = 0
            test_prompts = MultiturnTestPrompts(risk_name=risk.risk, test_prompts=[])
            ## Generate Multi Turn prompt
            for mprompt in _prompt_gen.generate(risk_name=risk.risk):
                test_prompt = self._convert_multi_turn_to_test_prompt(
                    module_name=dataset, 
                    multi_turn=mprompt,
                    risk_name=risk.risk
                )

                test_prompts.test_prompts.append(test_prompt)
                total_prompts += 1
                total_prompts_per_risk += 1

                if total_prompts >= max_prompts:
                    break

                if total_prompts_per_risk >= max_prompts_per_plugin:
                    break

            if len(test_prompts.test_prompts) > 0:
                yield test_prompts

            if total_prompts >= max_prompts:
                return

    def _convert_multi_turn_to_test_prompt(
        self, module_name: str, 
        multi_turn: MultiTurnConversation,
        risk_name:str
    ) -> MultiTurnTestPrompt:
        ## Return all the turns including assistant as classification models may need response
        filtered_turns = multi_turn.turns

        # Remove the last turn if it's from the assistant
        # filtered_turns = (
        #     multi_turn.turns[:-1]
        #     if multi_turn.turns and multi_turn.turns[-1].role == "ASSISTANT"
        #     else multi_turn.turns
        # )


        return MultiTurnTestPrompt(
            turns=filtered_turns,  # Copy conversation turns without the last assistant turn
            evaluation_method=multi_turn.evaluation_hint,  # Assign evaluation hint
            plugin_id=risk_name,
            policy=multi_turn.policy,
            goal=multi_turn.goal,  # Assign goal
            strategy=multi_turn.goal,  # Use base_prompt as strategy
            module_name=module_name,
            base_prompt=multi_turn.base_prompt,
            complexity=multi_turn.complexity,
            jailbreak=multi_turn.jailbreak,
            unsafe=multi_turn.unsafe, 
        )
