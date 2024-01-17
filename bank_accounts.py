class BalanceException(Exception):
    pass


class BankAccount:
    def __init__(self, initial_amount, acct_name, min_balance=0):
        self.balance = initial_amount
        self.name = acct_name
        self.min_balance = min_balance
        self.is_blocked = False
        self.transaction_history = []
        self.log_transaction('Account opened', initial_amount)
        print(f"\nAccount '{self.name}' created.\nBalance = ${self.balance:.2f}")

    def create_child_account(self, initial_amount, child_name):
        if self.is_blocked:
            print(f"\nAccount '{self.name}' is currently blocked and cannot create a child account.")
            return None
        child_account = ChildAccount(initial_amount, child_name, parent_account=self)
        print(f"\nChild account '{child_account.name}' created under parent account '{self.name}'.")
        return child_account

    def log_transaction(self, action, amount):
        self.transaction_history.append((action, amount))

    def get_balance(self):
        if self.is_blocked:
            print(f"\nAccount '{self.name}' is currently blocked.")
            return
        print(f"\nAccount '{self.name}' balance = ${self.balance:.2f}")

    def deposit(self, amount):
        if self.is_blocked:
            print(f"\nAccount '{self.name}' is currently blocked.")
            return
        if amount <= 0:
            raise BalanceException("Deposit amount must be positive.")
        self.balance += amount
        self.log_transaction('Deposit', amount)
        print("\nDeposit complete.")
        self.get_balance()

    def withdraw(self, amount):
        if amount <= 0:
            raise BalanceException("Withdrawal amount must be positive.")
        if self.balance - amount < 0:
            raise BalanceException(f"Insufficient funds in account '{self.name}'.")
        self.balance -= amount
        self.log_transaction('Withdraw', -amount)
        print("\nWithdraw complete.")
        self.check_minimum_balance()

    def check_minimum_balance(self):
        if self.balance < self.min_balance:
            self.is_blocked = True
            print(f"\nAccount '{self.name}' has fallen below the minimum balance and is now blocked.")

    def unblock_account(self):
        if self.balance >= self.min_balance:
            self.is_blocked = False
            print(f"\nAccount '{self.name}' is now unblocked.")
        else:
            print(f"\nAccount '{self.name}' cannot be unblocked. Balance is below the minimum requirement.")

    def viable_transaction(self, amount):
        if self.balance < amount:
            raise BalanceException(f"Insufficient funds for the transaction in account '{self.name}'.")

    def transfer(self, amount, account):
        if self.is_blocked:
            print(f"\nAccount '{self.name}' is currently blocked.")
            return
        if amount <= 0:
            raise BalanceException("Transfer amount must be positive.")
        if self == account:
            raise BalanceException("Cannot transfer to the same account.")
        self.viable_transaction(amount)
        self.withdraw(amount)
        account.deposit(amount)
        self.log_transaction('Transfer', amount)
        print('\nTransfer complete!')
        self.check_minimum_balance()

    def view_transaction_history(self):
        for action, amount in self.transaction_history:
            print(f"{action}: ${amount:.2f}")

    def close_account(self):
        if self.is_blocked:
            print(f"\nAccount '{self.name}' is currently blocked and cannot be closed.")
            return
        # Check if the balance is zero or within allowed limit
        if self.balance != 0 and self.balance < self.min_balance:
            print(f"\nAccount '{self.name}' cannot be closed because the balance is below the minimum requirement.")
            return
        # Perform account closure steps
        self.is_blocked = True  # Block the account
        self.log_transaction('Account Closed', 0)  # Log the closure transaction
        print(f"\nAccount '{self.name}' has been closed.")


class InterestRewardsAcct(BankAccount):
    def __init__(self, initial_amount, acct_name, min_balance=0):
        super().__init__(initial_amount, acct_name, min_balance)

    def deposit(self, amount):
        if self.is_blocked:
            print(f"\nAccount '{self.name}' is currently blocked.")
            return
        if amount <= 0:
            raise BalanceException("Deposit amount must be positive.")
        bonus_amount = amount * 0.05
        self.balance += amount + bonus_amount
        self.log_transaction('Interest Deposit', amount + bonus_amount)
        print("\nInterest deposit complete.")
        self.get_balance()


class SavingsAcct(InterestRewardsAcct):
    def __init__(self, initial_amount, acct_name, fee=5, min_balance=0):
        super().__init__(initial_amount, acct_name, min_balance)
        self.fee = fee

    def withdraw(self, amount):
        total_amount = amount + self.fee
        if total_amount <= 0:
            raise BalanceException("Withdrawal amount must be positive.")
        if self.balance - total_amount < 0:
            raise BalanceException(f"Insufficient funds in account '{self.name}'.")
        self.balance -= total_amount
        self.log_transaction('Withdraw with Fee', -total_amount)
        print("\nWithdraw complete with fee.")
        self.check_minimum_balance()

        # Check for minimum balance after withdrawal
        if self.balance < self.min_balance:
            self.is_blocked = True
            print(f"Account '{self.name}' has been blocked due to falling below the minimum balance.")
            raise BalanceException(f"Insufficient funds in account '{self.name}'.")

class ChildAccount(BankAccount):
    def __init__(self, initial_amount, acct_name, parent_account, min_balance=0):
        super().__init__(initial_amount, acct_name, min_balance)
        self.parent_account = parent_account

    def transfer_to_parent(self, amount):
        if self.is_blocked:
            print(f"\nChild account '{self.name}' is currently blocked.")
            return
        if amount <= 0:
            raise BalanceException("Transfer amount must be positive.")
        self.viable_transaction(amount)
        self.withdraw(amount)
        self.parent_account.deposit(amount)
        self.log_transaction('Transfer to Parent', amount)
        print(f'\nTransfer to parent account complete: ${amount:.2f}')
