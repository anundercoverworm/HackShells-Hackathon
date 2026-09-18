import os
from urllib.parse import quote

import altair as alt
import pandas as pd
import requests
import streamlit as st

# Configure the browser page and use a wide layout for dashboard tables and cards.
st.set_page_config(
    page_title="Collection Tracker",
    page_icon="📦",
    layout="wide",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")


def get_json(url):
    # Perform a GET request and convert the successful response to Python data.
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def refresh_collection():
    # Load products and series into Streamlit session state.
    try:
        products = get_json(f"{API_BASE_URL}/api/products")
        series = get_json(f"{API_BASE_URL}/api/series")
        st.session_state.products = products
        st.session_state.series = series
        return products, series
    except requests.RequestException:
        st.session_state.products = []
        st.session_state.series = []
        return [], []


def refresh_inventories():
    # Load inventories and calculate the displayed value for each one.
    try:
        inventories = get_json(f"{API_BASE_URL}/api/inventories")
        summary = []
        for inventory in inventories:
            value_data = get_json(f"{API_BASE_URL}/api/inventories/{inventory['id']}/value")
            summary.append({
                "id": inventory["id"],
                "name": inventory["name"],
                "value": value_data.get("total_value", 0),
            })
        st.session_state.inventories = inventories
        st.session_state.inventory_summary = summary
    except requests.RequestException:
        st.session_state.inventories = []
        st.session_state.inventory_summary = []


def fetch_marketplace(product_name):
    # Request current marketplace listings for one product.
    try:
        url = f"{API_BASE_URL}/api/marketplace/{quote(product_name)}"
        return get_json(url)
    except requests.RequestException:
        return []


def fetch_market_history(product_name):
    # Request synthetic market history used by the market-value chart.
    try:
        url = f"{API_BASE_URL}/api/marketplace/{quote(product_name)}/history"
        return get_json(url)
    except requests.RequestException:
        return []


def fetch_price_history(product_id):
    # Request the user's recorded price history for one product.
    try:
        return get_json(f"{API_BASE_URL}/api/products/{product_id}/price-history")
    except requests.RequestException:
        return []


def api_post(path, payload):
    # Send a JSON POST request to the backend API.
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def api_delete(path):
    # Delete a resource through the backend API.
    response = requests.delete(f"{API_BASE_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def make_change_chart(frame):
    # Prepare colors and fixed square dimensions for the change cards.
    chart_data = frame[["name", "Change"]].copy()
    chart_data["Change"] = pd.to_numeric(chart_data["Change"], errors="coerce").fillna(0.0)
    chart_data["fill_color"] = chart_data["Change"].apply(lambda value: "#22c55e" if value >= 0 else "#ef4444")
    chart_data["text_color"] = chart_data["Change"].apply(lambda value: "#15803d" if value >= 0 else "#b91c1c")
    chart_data["square_size"] = 68
    return chart_data


def render_change_cards(frame):
    # Render one equal-sized colored card for every product.
    chart_data = make_change_chart(frame)
    if chart_data.empty:
        st.info("No products to compare.")
        return

    cols = st.columns(len(chart_data))
    for col, row in zip(cols, chart_data.itertuples(index=False)):
        with col:
            value_text = f"+${row.Change:,.2f}" if row.Change >= 0 else f"-${abs(row.Change):,.2f}"
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    justify-content:center;
                    gap:10px;
                    padding:14px 10px 12px 10px;
                    min-height:170px;
                    border:1px solid rgba(15, 23, 42, 0.10);
                    border-radius:16px;
                    background:rgba(255,255,255,1);
                    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
                    text-align:center;
                ">
                    <div style="font-size:11px; font-weight:700; color:#334155; line-height:1.2; min-height:30px;">{row.name}</div>
                    <div style="
                        width:{int(row.square_size)}px;
                        height:{int(row.square_size)}px;
                        background:{row.fill_color};
                        border-radius:12px;
                        border:2px solid rgba(255,255,255,0.9);
                        box-shadow: inset 0 1px 0 rgba(255,255,255,0.35), 0 6px 12px rgba(15, 23, 42, 0.10);
                    "></div>
                    <div style="color:{row.text_color}; font-weight:800; font-size:12px; letter-spacing:0.02em;">{value_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def get_market_change_for_product(product):
    # Compare the latest market value with the user's purchase price.
    market_history = fetch_market_history(product["name"])
    if market_history:
        latest_market_value = float(market_history[-1].get("estimated_market_value", market_history[-1].get("market_value", product.get("current_price", 0))))
        return latest_market_value - float(product.get("purchase_price", 0))

    market_data = fetch_marketplace(product["name"])
    if market_data:
        market_value = float(market_data[0].get("estimated_market_value", product.get("current_price", 0)))
        return market_value - float(product.get("purchase_price", 0))

    return float(product.get("current_price", product.get("purchase_price", 0))) - float(product.get("purchase_price", 0))


# Load each data group once per Streamlit session.
if "products" not in st.session_state:
    refresh_collection()

if "series" not in st.session_state:
    refresh_collection()

if "inventories" not in st.session_state:
    refresh_inventories()

if "page" not in st.session_state:
    st.session_state.page = "Home"

products = st.session_state.products
series_list = st.session_state.series

total_value = sum(product.get("current_price", 0) for product in products)
total_products = len(products)
price_changes = sum(1 for product in products if product.get("purchase_price") != product.get("current_price"))


# The home page provides the main navigation shortcuts.
if st.session_state.page == "Home":
    st.title("📦 Collection Tracker")
    st.write("👋 Welcome to Collection Tracker!")
    st.write("Manage your collection and track product prices all in one place.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Current Collection Value", f"${total_value:,.2f}")
    with col2:
        st.metric("📦 Products in Collection", total_products)

    st.divider()
    st.subheader("What would you like to do?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()

        if st.button("📦 Products", use_container_width=True):
            st.session_state.page = "Products"
            st.rerun()

        if st.button("➕ Add Product", use_container_width=True):
            st.session_state.page = "Add Product"
            st.rerun()

    with col2:
        if st.button("🏷️ Collection Series", use_container_width=True):
            st.session_state.page = "Collection Series"
            st.rerun()

else:
    # All secondary pages share the sidebar navigation.
    pages = ["Dashboard", "Products", "Add Product", "Collection Series"]
    st.sidebar.title("📦 Collection Tracker")

    selected_page = st.sidebar.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.page),
        key="navigation",
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    if st.session_state.page == "Dashboard":
        # Dashboard combines collection totals, charts, marketplace data, and inventory values.
        st.title("📊 Dashboard")
        st.write("Manage your collection and track product prices.")
        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Collection Value", f"${total_value:,.2f}")
        with col2:
            st.metric("Products", total_products)
        with col3:
            st.metric("Price Changes", price_changes)

        st.divider()
        st.subheader("My Collection")

        if products:
            # Build a table with market-based change values for the collection.
            df = pd.DataFrame(products)
            df["Change"] = df.apply(get_market_change_for_product, axis=1)
            df["Change %"] = (df["Change"] / df["purchase_price"] * 100)

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.subheader("📈 Historical Price Trend")
            # Show user price history and market history on the same timeline.
            history_product = st.selectbox(
                "Select a product to view its price history",
                [item["name"] for item in products],
                key="dashboard_history_product",
            )
            selected_product = next(item for item in products if item["name"] == history_product)
            history_data = fetch_price_history(selected_product["id"])
            market_history = fetch_market_history(selected_product["name"])

            if history_data or market_history:
                frames = []
                if history_data:
                    history_df = pd.DataFrame(history_data)
                    history_df["date"] = pd.to_datetime(history_df["date"])
                    history_df = history_df.rename(columns={"price": "product_value"})[["date", "product_value"]]
                    frames.append(history_df)
                if market_history:
                    market_df = pd.DataFrame(market_history)
                    market_df["date"] = pd.to_datetime(market_df["date"])
                    market_df = market_df.rename(columns={"estimated_market_value": "market_value"})[["date", "market_value"]]
                    frames.append(market_df)

                if frames:
                    combined_df = frames[0]
                    for frame in frames[1:]:
                        combined_df = combined_df.merge(frame, on="date", how="outer")
                    combined_df = combined_df.sort_values("date")
                    st.line_chart(combined_df.set_index("date"))
            else:
                st.info("This product does not have historical price entries yet.")

            st.subheader("📊 Price Change by Product")
            # Use the same market-change metric as the table above.
            render_change_cards(df)

            st.subheader("📦 Inventory Overview")
            # Display the current value of every available inventory.
            inventory_summary = st.session_state.get("inventory_summary", [])
            if inventory_summary:
                cols = st.columns(len(inventory_summary))
                for col, inventory in zip(cols, inventory_summary):
                    with col:
                        st.metric(inventory["name"], f"${inventory['value']:,.2f}")
            else:
                st.info("No inventories available yet.")

            st.subheader("🛍️ Marketplace Snapshot")
            # Show seller listings for a product selected by the user.
            market_product = st.selectbox("Select product", [item["name"] for item in products], key="market_product_select")
            market_data = fetch_marketplace(market_product)
            if market_data:
                latest_listing = market_data[0]
                st.metric("Estimated Market Value", f"${latest_listing['estimated_market_value']:,.2f}")
                market_df = pd.DataFrame(latest_listing["listings"])
                st.dataframe(market_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Marketplace data is not available right now.")
        else:
            st.info("Your collection is empty. Add a product to get started.")

    elif st.session_state.page == "Products":
        # Products page lists records and provides deletion controls and history charts.
        st.title("📦 Products")
        st.write("View and manage the products in your collection.")

        if "product_removed" in st.session_state:
            st.success(f"'{st.session_state.product_removed}' was removed from your collection.")
            del st.session_state.product_removed

        if not products:
            st.info("Your collection is empty.")
        else:
            for index, product in enumerate(products):
                # Each product block contains details, history, and delete confirmation.
                st.subheader(product["name"])
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                with col1:
                    st.write(f"**Series:** {product['series']}")
                with col2:
                    st.write(f"**Purchase Price:** ${product['purchase_price']:.2f}")
                with col3:
                    change = product["current_price"] - product["purchase_price"]
                    st.write(f"**Current Price:** ${product['current_price']:.2f}")
                    if change > 0:
                        st.caption(f"📈 +${change:.2f}")
                    elif change < 0:
                        st.caption(f"📉 ${change:.2f}")
                    else:
                        st.caption("No price change")
                with col4:
                    if st.button("🗑️", key=f"delete_{index}", help="Remove product"):
                        st.session_state.product_to_delete = index
                        st.rerun()

                history_response = fetch_price_history(product["id"])
                market_history = fetch_market_history(product["name"])
                if history_response or market_history:
                    frames = []
                    if history_response:
                        history_df = pd.DataFrame(history_response)
                        history_df["date"] = pd.to_datetime(history_df["date"])
                        history_df = history_df.rename(columns={"price": "product_value"})[["date", "product_value"]]
                        frames.append(history_df)
                    if market_history:
                        market_df = pd.DataFrame(market_history)
                        market_df["date"] = pd.to_datetime(market_df["date"])
                        market_df = market_df.rename(columns={"estimated_market_value": "market_value"})[["date", "market_value"]]
                        frames.append(market_df)

                    if frames:
                        combined_df = frames[0]
                        for frame in frames[1:]:
                            combined_df = combined_df.merge(frame, on="date", how="outer")
                        combined_df = combined_df.sort_values("date")
                        st.line_chart(combined_df.set_index("date"))

                if "product_to_delete" in st.session_state and st.session_state.product_to_delete == index:
                    st.warning(f"Are you sure you want to remove '{product['name']}' from your collection?")
                    confirm_col1, confirm_col2 = st.columns(2)

                    with confirm_col1:
                        if st.button("Yes, remove it", key=f"confirm_delete_{index}", type="primary"):
                            api_delete(f"/api/products/{product['id']}")
                            st.session_state.product_removed = product["name"]
                            del st.session_state.product_to_delete
                            refresh_collection()
                            st.rerun()

                    with confirm_col2:
                        if st.button("Cancel", key=f"cancel_delete_{index}"):
                            del st.session_state.product_to_delete
                            st.rerun()

                st.divider()

    elif st.session_state.page == "Add Product":
        # Add Product validates form input before sending a new record to the API.
        st.title("➕ Add Product")
        st.write("Add a new product to your collection.")

        if "product_added" in st.session_state:
            st.success(f"'{st.session_state.product_added}' was added successfully!")
            if st.session_state.get("series_created"):
                st.info(f"🏷️ New series '{st.session_state.series_created}' was created automatically.")
                del st.session_state.series_created
            del st.session_state.product_added

        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            series = st.text_input("Collection Series")
            purchase_price = st.number_input("Purchase Price", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add Product", type="primary")

        if submitted:
            # Validate required fields before creating the product and its series.
            if not name.strip():
                st.error("Please enter a product name.")
            elif not series.strip():
                st.error("Please enter a collection series.")
            elif purchase_price <= 0:
                st.error("Please enter a purchase price greater than $0.")
            else:
                product_name = name.strip()
                series_name = series.strip()

                existing_series = next((existing for existing in series_list if existing.lower() == series_name.lower()), None)
                if existing_series is None:
                    api_post("/api/series", {"name": series_name})
                    st.session_state.series_created = series_name

                payload = {
                    "name": product_name,
                    "series": series_name,
                    "purchase_price": float(purchase_price),
                    "current_price": float(purchase_price),
                    "inventory_id": 1,
                    "brand": "Unknown",
                    "category": "Collectible",
                }

                api_post("/api/products", payload)
                st.session_state.product_added = product_name
                refresh_collection()
                refresh_inventories()
                st.rerun()

    elif st.session_state.page == "Collection Series":
        # Collection Series groups products and summarizes their combined value.
        st.title("🏷️ Collection Series")
        st.write("Manage your collection series and view the value of each series.")
        st.divider()

        st.subheader("Create a New Series")
        with st.form("create_series_form"):
            new_series_name = st.text_input("Series Name")
            create_series = st.form_submit_button("Create Series", type="primary")

        if create_series:
            # Avoid creating duplicate series names with different capitalization.
            clean_series_name = new_series_name.strip()
            if clean_series_name == "":
                st.error("Please enter a series name.")
            elif any(existing.lower() == clean_series_name.lower() for existing in series_list):
                st.warning(f"The series '{clean_series_name}' already exists.")
            else:
                api_post("/api/series", {"name": clean_series_name})
                st.success(f"Series '{clean_series_name}' created successfully!")
                refresh_collection()
                st.rerun()

        st.divider()
        st.subheader("Your Series")

        if not series_list:
            st.info("You don't have any collection series yet.")
        else:
            selected_series = st.selectbox("Select a series", series_list)
            series_products = [product for product in products if product["series"].lower() == selected_series.lower()]
            series_purchase_value = sum(product["purchase_price"] for product in series_products)
            series_current_value = sum(product["current_price"] for product in series_products)
            series_change = series_current_value - series_purchase_value
            series_change_percent = (series_change / series_purchase_value * 100) if series_purchase_value else 0

            st.subheader(f"📦 {selected_series}")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Products", len(series_products))
            with col2:
                st.metric("Purchase Value", f"${series_purchase_value:,.2f}")
            with col3:
                st.metric("Current Value", f"${series_current_value:,.2f}")
            with col4:
                st.metric("Change", f"${series_change:,.2f}", delta=f"{series_change_percent:.2f}%")

            if series_products:
                # Display products, history, and change cards for the selected series.
                st.subheader("Products in this Series")
                series_df = pd.DataFrame(series_products)
                series_df["Change"] = series_df.apply(get_market_change_for_product, axis=1)
                st.dataframe(series_df, use_container_width=True, hide_index=True)

                st.subheader("📈 Historical Price Trend")
                series_history_product = st.selectbox(
                    "Select a product from this series",
                    [item["name"] for item in series_products],
                    key="series_history_product",
                )
                selected_series_product = next(item for item in series_products if item["name"] == series_history_product)
                series_history_data = fetch_price_history(selected_series_product["id"])
                if series_history_data:
                    series_history_df = pd.DataFrame(series_history_data)
                    series_history_df["date"] = pd.to_datetime(series_history_df["date"])
                    series_history_df = series_history_df.sort_values("date")
                    st.line_chart(series_history_df.set_index("date")["price"])
                else:
                    st.info("This series product does not have price history yet.")

                st.subheader("📊 Price Changes in Series")
                render_change_cards(series_df)
            else:
                st.info(f"The series '{selected_series}' does not have any products yet.")