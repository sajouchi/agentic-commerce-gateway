from time import sleep
from uuid import uuid4
import streamlit as st

from app.agent.agent_state_graph import (
    initiate_graph,
    human_response
)
from app.db.sellerPayments import fetch_paymentStatusByLinkID

def get_state_value(state, key, default=None):
    if state is None:
        return default

    if isinstance(state, dict):
        return state.get(key, default)

    return getattr(state, key, default)

def app():
    # Page config
    st.set_page_config(
        page_title="Agent Commerce Gateway",
        page_icon="🤖",
        layout="wide"
    )

    # Session state
    if "thread" not in st.session_state:
        st.session_state.thread = {
            "configurable": {
                "thread_id": f"id-{uuid4()}"
            }
        }

    if "graph_state" not in st.session_state:
        st.session_state.graph_state = None

    if "started" not in st.session_state:
        st.session_state.started = False

    # Header
    st.title("👾 Agent Commerce Gateway")

    st.caption(
        "AI Buyer → Search → Offer Evaluation → Negotiate → Checkout"
    )

    st.divider()

    # Main columns
    buyer_col, gateway_col = st.container(), st.container()

    # Buyer panel
    with buyer_col:

        st.subheader("🔍Search for Product...")

        buyer_request = st.text_area(
            "What you looking for?",
            value=(
                "I need 250 wireless headphones "
                "under ₹1700 each."
            ),
            height=130
        )

        if st.button(
            "🚀 Start Simulation",
            type="primary",
            use_container_width=True
        ):

            # New thread
            st.session_state.thread = {
                "configurable": {
                    "thread_id": f"streamlit-{uuid4()}"
                }
            }

            progress = st.progress(
                0,
                text="🚀 Starting Agent Commerce Gateway..."
            )

            progress.progress(
                20,
                text="🧠 Extracting buyer intent..."
            )

            sleep(2)

            progress.progress(
                40,
                text="🔎 Searching product catalog..."
            )

            sleep(2)

            progress.progress(
                60,
                text="🛡️ Evaluating offer..."
            )

            sleep(1)

            progress.progress(
                80,
                text="🤝 Negotiating offer..."
            )

            # Run graph
            state = initiate_graph(
                buyer_request,
                st.session_state.thread
            )

            progress.progress(
                100,
                text="✅ Gateway processing complete"
            )

            sleep(1)

            st.session_state.graph_state = state
            st.session_state.started = True

            st.rerun()

    # Gateway panel
    with gateway_col:

        st.subheader("⚙️ Gateway")

        if not st.session_state.started:

            st.info(
                "Waiting for a buyer request..."
            )

        else:

            st.success(
                "Gateway processed the request"
            )

            state = st.session_state.graph_state

            # Intent
            st.write("### 🧠 Buyer Intent")

            filters = get_state_value(
                state,
                "filters"
            )

            if filters:

                st.write(
                    f"**Quantity:** "
                    f"{get_state_value(filters, 'qty', '-')}"
                )

                st.write(
                    f"**Target Price:** "
                    f"₹{get_state_value(filters, 'price', '-')}"
                )

                st.write(
                    f"**Brand:** "
                    f"{get_state_value(filters, 'brand', '-')}"
                )

            # Product
            results = get_state_value(
                state,
                "results",
                []
            )

            if results:

                product = results[0]
                
                st.write("### 📦 Matched Product")

                st.write(
                    f"**SKU:** "
                    f"{get_state_value(product, 'sku', '-')}"
                )

                st.write(
                    f"Product: "
                    f"{str(get_state_value(product, 'item', '-'))}"
                )

        # Negotiation
        if st.session_state.started:

            state = st.session_state.graph_state

            negotiation = get_state_value(
                state,
                "negotiation",
                []
            )

            if negotiation:
                negotiation_response = get_state_value(
                    state,
                    "negotiationResponse",
                    ""
                )

                if negotiation_response:

                    st.chat_message("assistant").write(
                        negotiation_response
                    )

                st.divider()

                st.subheader("🤝 Negotiation")

                latest = negotiation[-1]

                counter_price = get_state_value(
                    latest,
                    "counterPrice"
                )

                qty = get_state_value(
                    latest,
                    "qty",
                    "-"
                )

                reason = get_state_value(
                    latest,
                    "reason",
                    ""
                )

                if counter_price is not None:

                    st.info(
                        f"Gateway counter-offer: "
                        f"**₹{counter_price} / unit**"
                    )

                    st.write(
                        f"Quantity: **{qty}**"
                    )

                    if reason:
                        st.caption(reason)

                    st.divider()

                    response_col1, response_col2 = st.columns(2)

                    with response_col1:

                        if st.button(
                            "✅ Accept",
                            use_container_width=True
                        ):

                            with st.spinner(
                                "Processing acceptance...", show_time=True
                            ):

                                state = human_response(
                                    "I accept the offer",
                                    st.session_state.thread
                                )

                            st.session_state.graph_state = state

                            st.rerun()

                    with response_col2:

                        if st.button(
                            "❌ Reject",
                            use_container_width=True
                        ):

                            with st.spinner(
                                "Processing rejection...", show_time=True
                            ):

                                state = human_response(
                                    "I reject the offer",
                                    st.session_state.thread
                                )

                            st.session_state.graph_state = state

                            st.rerun()
 
    # Final result
    if st.session_state.started:

        state = st.session_state.graph_state

        final_result = get_state_value(
            state,
            "finalResult"
        )   
        
        final_agent_message = get_state_value(state, "acceptRejectResponse")

        if final_result:

            status = get_state_value(
                final_result,
                "status"
            )

            if status == "ACCEPT":

                st.success("🎉 DEAL ACCEPTED")
                
                st.write(f"{final_agent_message}")

                checkout_url = get_state_value(
                    final_result,
                    "checkoutUrl"
                )

                payment_link_id = get_state_value(
                    final_result,
                    "payment_link_id"
                )

                expires_in = get_state_value(
                    final_result,
                    "expiresIn"
                )

                # Payment link
                if checkout_url:
                    st.link_button(
                        "💳 Pay Now",
                        checkout_url,
                        use_container_width=True
                    )

                if expires_in:
                    st.caption(
                        f"Payment link expires in {expires_in}"
                    )

                st.divider()

                # Check payment
                if st.button(
                    "🔍 Check Payment Status",
                    use_container_width=True
                ):

                    with st.spinner("Checking payment..."):

                        try:
                            payment_status = fetch_paymentStatusByLinkID(
                                payment_link_id=payment_link_id
                            )

                            if payment_status == "paid":

                                st.success(
                                    "✅ Payment Successful & Captured!"
                                )
                                st.balloons()

                            else:

                                st.warning(
                                    "⏳ Payment not captured yet."
                                )

                        except Exception as e:

                            st.error(
                                f"❌ Unable to verify payment: {e}"
                            )

            elif status == "REJECT":

                st.divider()
                st.error(f"**😥{str(final_agent_message)}**")

    # Reset
    st.divider()

    if st.button(
        "🔄 New Simulation",
        use_container_width=True
    ):
        
        # Fresh conversation
        st.session_state.thread = {
            "configurable": {
                "thread_id": f"streamlit-{uuid4()}"
            }
        }

        with st.spinner("New session processing", show_time=True):
            
            st.session_state.graph_state = None
            st.session_state.started = False

            st.rerun()
