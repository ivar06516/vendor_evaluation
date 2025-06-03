import os

from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from vendor_evaluation_tool import update_vendor_scores
os.environ["OPENAI_API_KEY"] = "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"

from pydantic import BaseModel

class KPISchema(BaseModel):
    total_units_received: int
    defective_units: int
    returned_units: int
    on_time_shipments: int
    total_shipments: int
    vendor_price: float
    target_price: float
    avg_response_time: int
    expected_response_time: int
    passed_audits: int
    total_audits: int
    missing_docs: int
    required_docs: int

class VendorScoreInput(BaseModel):
    vendor_id: str
    kpi_input: KPISchema


@tool(args_schema=VendorScoreInput)
def score_vendor_json(vendor_id: str, kpi_input: KPISchema) -> str:
    """
      Evaluate vendor performance based on the provided KPIs
      and return a calculated score.
      """
    return update_vendor_scores(vendor_id, kpi_input.model_dump())


llm = ChatOpenAI()
agent = initialize_agent(
    tools=[score_vendor_json],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

kpi_input = {
    "total_units_received": 1000,
    "defective_units": 10,
    "returned_units": 20,
    "on_time_shipments": 180,
    "total_shipments": 200,
    "vendor_price": 9.5,
    "target_price": 10.0,
    "avg_response_time": 4,
    "expected_response_time": 6,
    "passed_audits": 3,
    "total_audits": 4,
    "missing_docs": 1,
    "required_docs": 5
}


response = agent.invoke({
    "input": {
        "vendor_id": "V12345",
        "kpi_input": kpi_input
    }
})

print("Response:", response)