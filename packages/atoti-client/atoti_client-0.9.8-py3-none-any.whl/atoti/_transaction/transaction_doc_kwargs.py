TRANSACTION_DOC_KWARGS = {
    "allow_nested": """allow_nested: Whether to allow starting this transaction inside an already running one.

                When ``False``, an error will be raised if this transaction is started while another transaction is already running, regardless of that outer transaction's value of *allow_nested*.
                The benefit of passing ``False`` is that changes made in this transaction are guaranteed, if not rolled back, to be visible to the statements outside the transaction.
                The drawback is that it prevents splitting transaction steps in small composable functions.

                When nested transactions are allowed, changes made by inner transactions contribute transparently to the outer transaction and will only be committed when the outer transaction's context exits.
""",
}
