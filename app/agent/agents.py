import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_groq import ChatGroq

from app.schema.agent_schema import QueryOutput
from app.schema.allSchema import BuyersResponse
from app.agent.prompts.system_prompts import (intentSystemPrompt,counterOfferSystemPrompt,
                                              finalResponseSystemPrompt, buyerResponseSystemPrompt,
                                              successPaymentMessageSystemPrompt)
load_dotenv()

os.environ['GROQ_API_KEY']=os.getenv("groq_api_key")

### initializing different agents for different tasks ###

#### Intent Based Query Generator Agent ###
intentPrompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=intentSystemPrompt),
                HumanMessagePromptTemplate.from_template("{user_input}")
            ]
        )

intentModel = ChatGroq(model="openai/gpt-oss-20b")
intentAgent = intentPrompt | intentModel\
                                        .with_structured_output(QueryOutput,
                                                                method="json_mode")

#### Friendly Negotiation Agent ###

counterOfferPrompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(content=counterOfferSystemPrompt),
                        HumanMessagePromptTemplate.from_template("{user_input}")
                    ]
                    )

counterOfferModel = ChatGroq(model="openai/gpt-oss-20b")
counterOfferAgent = counterOfferPrompt | counterOfferModel

### Acception or Rejection or Payment Checkout Response Agent ###

finalResponsePrompt = ChatPromptTemplate.from_messages(

                        [
                            SystemMessage(content=finalResponseSystemPrompt),
                            HumanMessagePromptTemplate.from_template("{user_input}")
                        ]
                        
                        )

finalResponseModel = ChatGroq(model="openai/gpt-oss-20b")
finalResponseAgent = finalResponsePrompt | finalResponseModel

### Buyers Response After Counter Offers (negotiation Stage 2nd step) ###

buyerResponsePrompt = ChatPromptTemplate.from_messages(

                        [
                            SystemMessage(content=buyerResponseSystemPrompt),
                            HumanMessagePromptTemplate.from_template("{user_input}")
                        ]
                        
                        )

buyerResponseModel = ChatGroq(model="openai/gpt-oss-20b")
buyerResponseAgent = buyerResponsePrompt | buyerResponseModel\
                                                 .with_structured_output(schema=BuyersResponse,
                                                                         method="json_mode")

# payment link appear response create agent or simple bot

successPaymentMessagePrompt = ChatPromptTemplate([("ai",f"{successPaymentMessageSystemPrompt}"),
                                                  ("human",("{user_input}"))])

successPaymentMessageModel = ChatGroq(model="openai/gpt-oss-20b")
successPaymentMessageAgent = successPaymentMessagePrompt | successPaymentMessageModel