import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import os

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

FILE_NAME = "expenses.csv"
COLUMNS = ["Date", "Category", "Amount", "Description"]

# Load saved expenses
if os.path.exists(FILE_NAME):
    expenses = pd.read_csv(FILE_NAME)
    for column in COLUMNS:
        if column not in expenses.columns:
            expenses[column] = ""
    expenses = expenses[COLUMNS]
else:
    expenses = pd.DataFrame(columns=COLUMNS)


def save_expenses():
    expenses.to_csv(FILE_NAME, index=False)


st.title("💰 Personal Expense Tracker")
st.write("Add, view and manage your daily expenses.")

# Add expense
st.header("Add a New Expense")

with st.form("expense_form"):
    expense_date = st.date_input("Date", value=date.today())
    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Bills", "Other"]
    )
    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=1.0
    )
    description = st.text_input("Description")

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            new_expense = pd.DataFrame([{
                "Date": expense_date.strftime("%Y-%m-%d"),
                "Category": category,
                "Amount": amount,
                "Description": description
            }])

            expenses = pd.concat(
                [expenses, new_expense],
                ignore_index=True
            )
            save_expenses()
            st.success("Expense added successfully!")
            st.rerun()

st.divider()

# Display expenses
st.header("All Expenses")

if not expenses.empty:
    expenses["Amount"] = pd.to_numeric(
        expenses["Amount"], errors="coerce"
    ).fillna(0)

    st.dataframe(expenses, use_container_width=True)

    # Total expenses
    total = expenses["Amount"].sum()
    st.metric("Total Expenses", f"₹{total:,.2f}")

    # Category summary
    st.subheader("Category-wise Summary")
    summary = expenses.groupby("Category")["Amount"].sum()
    st.dataframe(summary, use_container_width=True)

    # Budget checking
    st.subheader("Budget Checker")
    budget = st.number_input(
        "Enter your monthly budget (₹)",
        min_value=0.0,
        step=500.0
    )

    if budget > 0:
        remaining = budget - total

        if remaining >= 0:
            st.success(f"Remaining budget: ₹{remaining:,.2f}")
        else:
            st.error(f"Budget exceeded by ₹{abs(remaining):,.2f}")

    # Expense chart
    st.subheader("Expenses by Category")
    fig, ax = plt.subplots()
    summary.plot(kind="bar", ax=ax)
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Expenses by Category")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)
    plt.close(fig)

else:
    st.info("No expenses available. Add your first expense above.")
