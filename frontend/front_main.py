import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Collection Tracker",
    page_icon="📦",
    layout="wide"
)

# ---------------------------------
# Default data
# ---------------------------------

default_products = [
    {
        "name": "Nintendo Switch 2",
        "series": "Nintendo",
        "purchase_price": 450.00,
        "current_price": 500.00
    },
    {
        "name": "Zelda Collector's Edition",
        "series": "The Legend of Zelda",
        "purchase_price": 80.00,
        "current_price": 95.00
    },
    {
        "name": "Pokémon Figure",
        "series": "Pokémon",
        "purchase_price": 35.00,
        "current_price": 30.00
    }
]

default_series = [
    "Nintendo",
    "The Legend of Zelda",
    "Pokémon"
]

# ---------------------------------
# Session State
# ---------------------------------

if "products" not in st.session_state:
    st.session_state.products = default_products.copy()

if "series" not in st.session_state:
    st.session_state.series = default_series.copy()

if "page" not in st.session_state:
    st.session_state.page = "Home"


# ---------------------------------
# Current data
# ---------------------------------

products = st.session_state.products
series_list = st.session_state.series


# ---------------------------------
# Calculations
# ---------------------------------

total_value = sum(
    product["current_price"]
    for product in products
)

total_products = len(products)

price_changes = sum(
    1
    for product in products
    if product["purchase_price"] != product["current_price"]
)


# ---------------------------------
# Home
# ---------------------------------

if st.session_state.page == "Home":

    st.title("📦 Collection Tracker")

    st.write(
        "👋 Welcome to Collection Tracker!"
    )

    st.write(
        "Manage your collection and track product prices "
        "all in one place."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "💰 Current Collection Value",
            f"${total_value:,.2f}"
        )

    with col2:

        st.metric(
            "📦 Products in Collection",
            total_products
        )

    st.divider()

    st.subheader("What would you like to do?")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📊 Dashboard",
            use_container_width=True
        ):

            st.session_state.page = "Dashboard"
            st.rerun()

        if st.button(
            "📦 Products",
            use_container_width=True
        ):

            st.session_state.page = "Products"
            st.rerun()

        if st.button(
            "➕ Add Product",
            use_container_width=True
        ):

            st.session_state.page = "Add Product"
            st.rerun()

    with col2:

        if st.button(
            "🏷️ Collection Series",
            use_container_width=True
        ):

            st.session_state.page = "Collection Series"
            st.rerun()


# ---------------------------------
# Internal Pages
# ---------------------------------

else:

    # ---------------------------------
    # Sidebar
    # ---------------------------------

    pages = [
        "Dashboard",
        "Products",
        "Add Product",
        "Collection Series"
    ]

    st.sidebar.title("📦 Collection Tracker")

    selected_page = st.sidebar.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.page),
        key="navigation"
    )

    if selected_page != st.session_state.page:

        st.session_state.page = selected_page
        st.rerun()


    # ---------------------------------
    # Dashboard
    # ---------------------------------

    if st.session_state.page == "Dashboard":

        st.title("📊 Dashboard")

        st.write(
            "Manage your collection and track product prices."
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Collection Value",
                f"${total_value:,.2f}"
            )

        with col2:

            st.metric(
                "Products",
                total_products
            )

        with col3:

            st.metric(
                "Price Changes",
                price_changes
            )

        st.divider()

        st.subheader("My Collection")

        if products:

            df = pd.DataFrame(products)

            df["Change"] = (
                df["current_price"]
                - df["purchase_price"]
            )

            df["Change %"] = (
                df["Change"]
                / df["purchase_price"]
                * 100
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("📈 Price Changes")

            chart_data = df[["name", "Change"]].copy()

            chart = alt.Chart(
                chart_data
            ).mark_bar(
                size=35
            ).encode(
                x=alt.X(
                    "name:N",
                    title=None,
                    axis=alt.Axis(labelAngle=0)
                ),
                y=alt.Y(
                    "Change:Q",
                    title="Price Change ($)"
                ),
                tooltip=[
                    alt.Tooltip(
                        "name:N",
                        title="Product"
                    ),
                    alt.Tooltip(
                        "Change:Q",
                        title="Change",
                        format="$.2f"
                    )
                ]
            )

            st.altair_chart(
                chart,
                use_container_width=True
            )

        else:

            st.info(
                "Your collection is empty. "
                "Add a product to get started."
            )


    # ---------------------------------
    # Products
    # ---------------------------------

    elif st.session_state.page == "Products":

        st.title("📦 Products")

        st.write(
            "View and manage the products in your collection."
        )

        if "product_removed" in st.session_state:

            st.success(
                f"'{st.session_state.product_removed}' "
                "was removed from your collection."
            )

            del st.session_state.product_removed

        if not products:

            st.info(
                "Your collection is empty."
            )

        else:

            for index, product in enumerate(products):

                st.subheader(product["name"])

                col1, col2, col3, col4 = st.columns(
                    [2, 2, 2, 1]
                )

                with col1:

                    st.write(
                        f"**Series:** {product['series']}"
                    )

                with col2:

                    st.write(
                        f"**Purchase Price:** "
                        f"${product['purchase_price']:.2f}"
                    )

                with col3:

                    change = (
                        product["current_price"]
                        - product["purchase_price"]
                    )

                    st.write(
                        f"**Current Price:** "
                        f"${product['current_price']:.2f}"
                    )

                    if change > 0:

                        st.caption(
                            f"📈 +${change:.2f}"
                        )

                    elif change < 0:

                        st.caption(
                            f"📉 ${change:.2f}"
                        )

                    else:

                        st.caption(
                            "No price change"
                        )

                with col4:

                    if st.button(
                        "🗑️",
                        key=f"delete_{index}",
                        help="Remove product"
                    ):

                        st.session_state.product_to_delete = index
                        st.rerun()

                # ---------------------------------
                # Delete confirmation
                # ---------------------------------

                if (
                    "product_to_delete" in st.session_state
                    and
                    st.session_state.product_to_delete == index
                ):

                    st.warning(
                        f"Are you sure you want to remove "
                        f"'{product['name']}' from your collection?"
                    )

                    confirm_col1, confirm_col2 = st.columns(2)

                    with confirm_col1:

                        if st.button(
                            "Yes, remove it",
                            key=f"confirm_delete_{index}",
                            type="primary"
                        ):

                            removed_product = products.pop(index)

                            st.session_state.product_removed = (
                                removed_product["name"]
                            )

                            del st.session_state.product_to_delete

                            st.rerun()

                    with confirm_col2:

                        if st.button(
                            "Cancel",
                            key=f"cancel_delete_{index}"
                        ):

                            del st.session_state.product_to_delete

                            st.rerun()

                st.divider()


    # ---------------------------------
    # Add Product
    # ---------------------------------

    elif st.session_state.page == "Add Product":

        st.title("➕ Add Product")

        st.write(
            "Add a new product to your collection."
        )

        # ---------------------------------
        # Success message
        # ---------------------------------

        if "product_added" in st.session_state:

            st.success(
                f"'{st.session_state.product_added}' "
                "was added successfully!"
            )

            if st.session_state.get("series_created"):

                st.info(
                    f"🏷️ New series "
                    f"'{st.session_state.series_created}' "
                    "was created automatically."
                )

                del st.session_state.series_created

            del st.session_state.product_added


        # ---------------------------------
        # Add Product Form
        # ---------------------------------

        with st.form("add_product_form"):

            name = st.text_input(
                "Product Name"
            )

            series = st.text_input(
                "Collection Series"
            )

            purchase_price = st.number_input(
                "Purchase Price",
                min_value=0.0,
                step=0.01
            )

            submitted = st.form_submit_button(
                "Add Product",
                type="primary"
            )


        if submitted:

            if name.strip() == "":

                st.error(
                    "Please enter a product name."
                )

            elif series.strip() == "":

                st.error(
                    "Please enter a collection series."
                )

            elif purchase_price <= 0:

                st.error(
                    "Please enter a purchase price greater than $0."
                )

            else:

                product_name = name.strip()
                series_name = series.strip()

                # ---------------------------------
                # Check if series exists
                # ---------------------------------

                existing_series = next(
                    (
                        existing
                        for existing in series_list
                        if existing.lower() == series_name.lower()
                    ),
                    None
                )

                if existing_series is None:

                    series_list.append(
                        series_name
                    )

                    st.session_state.series_created = (
                        series_name
                    )

                    series_name = series_name

                else:

                    series_name = existing_series


                # ---------------------------------
                # Create product
                # ---------------------------------

                new_product = {
                    "name": product_name,
                    "series": series_name,
                    "purchase_price": purchase_price,
                    "current_price": purchase_price
                }

                st.session_state.products.append(
                    new_product
                )

                st.session_state.product_added = (
                    product_name
                )

                st.rerun()


    # ---------------------------------
    # Collection Series
    # ---------------------------------

    elif st.session_state.page == "Collection Series":

        st.title("🏷️ Collection Series")

        st.write(
            "Manage your collection series and view "
            "the value of each series."
        )

        st.divider()

        # ---------------------------------
        # Create new series
        # ---------------------------------

        st.subheader("Create a New Series")

        with st.form("create_series_form"):

            new_series_name = st.text_input(
                "Series Name"
            )

            create_series = st.form_submit_button(
                "Create Series",
                type="primary"
            )

        if create_series:

            clean_series_name = new_series_name.strip()

            if clean_series_name == "":

                st.error(
                    "Please enter a series name."
                )

            elif any(
                existing.lower() == clean_series_name.lower()
                for existing in series_list
            ):

                st.warning(
                    f"The series '{clean_series_name}' "
                    "already exists."
                )

            else:

                series_list.append(
                    clean_series_name
                )

                st.success(
                    f"Series '{clean_series_name}' "
                    "created successfully!"
                )

                st.rerun()


        st.divider()

        # ---------------------------------
        # Series list
        # ---------------------------------

        st.subheader("Your Series")

        if not series_list:

            st.info(
                "You don't have any collection series yet."
            )

        else:

            selected_series = st.selectbox(
                "Select a series",
                series_list
            )

            # ---------------------------------
            # Products in selected series
            # ---------------------------------

            series_products = [
                product
                for product in products
                if product["series"].lower()
                == selected_series.lower()
            ]

            series_purchase_value = sum(
                product["purchase_price"]
                for product in series_products
            )

            series_current_value = sum(
                product["current_price"]
                for product in series_products
            )

            series_change = (
                series_current_value
                - series_purchase_value
            )

            if series_purchase_value != 0:

                series_change_percent = (
                    series_change
                    / series_purchase_value
                    * 100
                )

            else:

                series_change_percent = 0


            # ---------------------------------
            # Series information
            # ---------------------------------

            st.subheader(
                f"📦 {selected_series}"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Products",
                    len(series_products)
                )

            with col2:

                st.metric(
                    "Purchase Value",
                    f"${series_purchase_value:,.2f}"
                )

            with col3:

                st.metric(
                    "Current Value",
                    f"${series_current_value:,.2f}"
                )

            with col4:

                st.metric(
                    "Change",
                    f"${series_change:,.2f}",
                    delta=f"{series_change_percent:.2f}%"
                )


            # ---------------------------------
            # Products in series
            # ---------------------------------

            if series_products:

                st.subheader(
                    "Products in this Series"
                )

                series_df = pd.DataFrame(
                    series_products
                )

                series_df["Change"] = (
                    series_df["current_price"]
                    - series_df["purchase_price"]
                )

                st.dataframe(
                    series_df,
                    use_container_width=True,
                    hide_index=True
                )

                # ---------------------------------
                # Series chart
                # ---------------------------------

                st.subheader(
                    "📈 Price Changes in Series"
                )

                series_chart_data = series_df[
                    ["name", "Change"]
                ].copy()

                series_chart = alt.Chart(
                    series_chart_data
                ).mark_bar(
                    size=35
                ).encode(
                    x=alt.X(
                        "name:N",
                        title=None,
                        axis=alt.Axis(labelAngle=0)
                    ),
                    y=alt.Y(
                        "Change:Q",
                        title="Price Change ($)"
                    ),
                    tooltip=[
                        alt.Tooltip(
                            "name:N",
                            title="Product"
                        ),
                        alt.Tooltip(
                            "Change:Q",
                            title="Change",
                            format="$.2f"
                        )
                    ]
                )

                st.altair_chart(
                    series_chart,
                    use_container_width=True
                )

            else:

                st.info(
                    f"The series '{selected_series}' "
                    "does not have any products yet."
                )