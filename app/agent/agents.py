import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_groq import ChatGroq

from app.agent.agent_schema import queryAgent_outputSchema
from app.schema.allSchema import buyersResponse
from app.agent.prompts.system_prompts import (intent_system_prompt,negotiation_system_prompt,
                                              end_bot_prompt, negotiation_buyer_response_prompt)
load_dotenv()

os.environ['GROQ_API_KEY']=os.getenv("groq_api_key")

# initializing different agents for different tasks

#### Intent Based Query Generator Agent ###
intent_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=intent_system_prompt),
                HumanMessagePromptTemplate.from_template("{user_input}")
            ]
        )

intent_retrive_model = ChatGroq(model="openai/gpt-oss-20b")
intent_retrive_model_with_schema = intent_retrive_model.with_structured_output(queryAgent_outputSchema,method="json_mode")
intent_retrieve_agent = intent_prompt | intent_retrive_model_with_schema

#### Friendly Negotiation Agent ###

negotiation_prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(content=negotiation_system_prompt),
                        HumanMessagePromptTemplate.from_template("{user_input}")
                    ]
                    )

negotiation_doing_agent = ChatGroq(model="openai/gpt-oss-20b")
negotiation_agent = negotiation_prompt | negotiation_doing_agent

### Acception or Rejection or Payment Checkout Response Agent ###

accept_reject_prompt = ChatPromptTemplate.from_messages(

                        [
                            SystemMessage(content=end_bot_prompt),
                            HumanMessagePromptTemplate.from_template("{user_input}")
                        ]
                        
                        )

accept_reject_doing_agent = ChatGroq(model="openai/gpt-oss-20b")
accept_reject_agent = accept_reject_prompt | accept_reject_doing_agent

### Buyers Response After Counter Offers (negotiation Stage 2nd step) ###

buyers_response_prompt = ChatPromptTemplate.from_messages(

                        [
                            SystemMessage(content=negotiation_buyer_response_prompt),
                            HumanMessagePromptTemplate.from_template("{user_input}")
                        ]
                        
                        )

buyers_response_model_agent = ChatGroq(model="openai/gpt-oss-20b")
buyers_response_with_schema = buyers_response_model_agent.with_structured_output(schema=buyersResponse,method="json_mode")
buyers_response_agent = buyers_response_prompt | buyers_response_with_schema
