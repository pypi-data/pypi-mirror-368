# from string import Template
# from typing import Dict, Optional
#
# from common.scenario import ScenarioIntent
#
#
# class ScenarioPhrase:
#     value: Template | str = ""
#
#     def get_text(self, **kwargs) -> str:
#         return self.value.substitute(**kwargs)
#
#
# class ScenarioPayload:
#     payload: dict = {}
#
#
# class ScenarioConnector:
#
#     def __init__(self, phrase: type(ScenarioPhrase), payload: ScenarioPayload):
#         self.intent: Optional[ScenarioIntent] = None
#         self.phrases: Dict[str, phrase] = {}
#         self.payload: Dict[str, payload] = {}
#
#     async def connect(self):
#         print(self.phrases)
#         print(type(self.phrases))
#
#
# c = ScenarioConnector(ScenarioPhrase, ScenarioPayload())
