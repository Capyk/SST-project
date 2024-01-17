import unittest
from bank_accounts import BankAccount, InterestRewardsAcct, SavingsAcct, BalanceException


class TestBankAccountFeatures(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(1000, 'TestAccount', min_balance=100)

    def test_account_blocking(self):
        # Withdraw an amount that brings the balance below the minimum but not below zero
        withdrawal_amount = self.account.balance - self.account.min_balance + 1
        # with self.assertRaises(BalanceException):
        self.account.withdraw(withdrawal_amount)
        self.assertTrue(self.account.is_blocked)

    def test_account_unblocking(self):
        withdrawal_amount = self.account.balance - self.account.min_balance + 1
        # with self.assertRaises(BalanceException):
        self.account.withdraw(withdrawal_amount)
        self.account.deposit(200)  # This should unblock the account
        self.assertFalse(self.account.is_blocked)

    def test_transaction_history(self):
        self.account.deposit(200)
        self.account.withdraw(100)
        expected_history = [
            ('Account opened', 1000),
            ('Deposit', 200),
            ('Withdraw', -100)
        ]
        self.assertEqual(self.account.transaction_history, expected_history)


class TestBankAccountMore(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(1000, 'TestAccount', min_balance=100)

    def test_negative_deposit(self):
        with self.assertRaises(BalanceException):
            self.account.deposit(-100)

    def test_transfer_to_blocked_account(self):
        recipient_account = BankAccount(500, 'RecipientAccount', min_balance=200)
        recipient_account.withdraw(400)  # This should block the recipient account
        # with self.assertRaises(BalanceException):
        self.account.transfer(200, recipient_account)

    def test_transfer_from_blocked_account(self):
        self.account.withdraw(950)  # This should block the account
        recipient_account = BankAccount(500, 'RecipientAccount')
        # with self.assertRaises(BalanceException):
        self.account.transfer(50, recipient_account)

class TestBankAccountEdgeCases(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(1000, 'EdgeCaseAccount', min_balance=50)

    def test_zero_deposit(self):
        with self.assertRaises(BalanceException):
            self.account.deposit(0)

    def test_zero_withdrawal(self):
        with self.assertRaises(BalanceException):
            self.account.withdraw(0)

    def test_large_transfer(self):
        large_amount = self.account.balance + 100  # More than available balance
        recipient_account = BankAccount(500, 'Recipient')
        with self.assertRaises(BalanceException):
            self.account.transfer(large_amount, recipient_account)

    def test_transfer_to_unblocked_account(self):
        recipient_account = BankAccount(500, 'Recipient', min_balance=1000)  # initially blocked
        recipient_account.deposit(1000)  # unblock the account
        self.account.transfer(100, recipient_account)
        self.assertEqual(recipient_account.balance, 1600)  # Check if transfer was successful



class TestInterestRewardsAcct(unittest.TestCase):

    def setUp(self):
        self.account = InterestRewardsAcct(1000, 'InterestAccount')

    def test_interest_deposit(self):
        self.account.deposit(100)
        self.assertEqual(self.account.balance, 1105)  # 1000 + 100 * 1.05

    def test_deposit_on_blocked_account(self):
        self.account.withdraw(950)  # This should block the account
        self.assertTrue(self.account.is_blocked)
        # with self.assertRaises(BalanceException):
        self.account.deposit(100)

    def test_interest_calculation_on_small_deposit(self):
        self.account.deposit(10)
        self.assertAlmostEqual(self.account.balance, 1010.5)  # 1000 + 10 * 1.05


class TestSavingsAcct(unittest.TestCase):

    def setUp(self):
        self.account = SavingsAcct(1000, 'SavingsAccount', min_balance=200)

    def test_withdraw_fee(self):
        self.account.withdraw(100)  # 100 + 5 fee
        self.assertEqual(self.account.balance, 895)  # 1000 - 105

    def test_minimum_balance(self):
        with self.assertRaises(BalanceException):
            self.account.withdraw(800)  # This should exceed the minimum balance

    def test_withdrawal_that_blocks_account(self):
        with self.assertRaises(BalanceException):
            self.account.withdraw(795)  # Withdrawal + fee brings below min_balance

    def test_deposit_on_blocked_account(self):
        self.account.withdraw(800)  # This should block the account

        with self.assertRaises(BalanceException):
            self.account.deposit(100)


class TestInterestRewardsAcctEdgeCases(unittest.TestCase):

    def setUp(self):
        self.account = InterestRewardsAcct(1000, 'InterestEdgeCaseAccount')

    def test_interest_on_zero_deposit(self):
        with self.assertRaises(BalanceException):
            self.account.deposit(0)

    def test_withdrawal_exceeding_balance(self):
        with self.assertRaises(BalanceException):
            self.account.withdraw(self.account.balance + 1)  # Withdraw more than balance

class TestSavingsAcctEdgeCases(unittest.TestCase):

    def setUp(self):
        self.account = SavingsAcct(1000, 'SavingsEdgeCaseAccount', min_balance=100)

    def test_exact_withdrawal_to_min_balance(self):
        self.account.withdraw(895)  # Withdraw to exactly min balance
        self.assertEqual(self.account.balance, 100)
        self.assertFalse(self.account.is_blocked)

    def test_withdrawal_just_over_min_balance(self):
        with self.assertRaises(BalanceException):
            self.account.withdraw(896)  # Just over the minimum balance

class TestBankAccountSequentialTransactions(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(1000, 'SequentialTransAccount', min_balance=50)

    def test_sequential_transactions(self):
        self.account.deposit(200)
        self.account.withdraw(100)
        self.account.deposit(50)
        self.account.withdraw(25)
        expected_final_balance = 1000 + 200 - 100 + 50 - 25
        self.assertEqual(self.account.balance, expected_final_balance)

class TestChildAccount(unittest.TestCase):

    def setUp(self):
        self.parent_account = BankAccount(1000, 'ParentAccount', min_balance=100)
        self.child_account = self.parent_account.create_child_account(500, 'ChildAccount')

    def test_child_account_creation(self):
        self.assertIsNotNone(self.child_account)
        self.assertEqual(self.child_account.name, 'ChildAccount')
        self.assertEqual(self.child_account.min_balance, 0)
        self.assertFalse(self.child_account.is_blocked)

    def test_transfer_to_parent(self):
        self.child_account.transfer_to_parent(200)
        self.assertEqual(self.child_account.balance, 300)
        self.assertEqual(self.parent_account.balance, 1200)

    def test_blocked_child_account_transfer_to_parent(self):
        self.child_account.withdraw(450)  # Block the child account
        with self.assertRaises(BalanceException):
            self.child_account.transfer_to_parent(100)
        self.assertEqual(self.child_account.balance, 50)
        self.assertEqual(self.parent_account.balance, 1000)

    def test_transfer_to_blocked_parent_account(self):
        self.parent_account.withdraw(900)  # Block the parent account
        # with self.assertRaises(BalanceException):
        self.child_account.transfer_to_parent(100)
        self.assertEqual(self.child_account.balance, 400)
        self.assertEqual(self.parent_account.balance, 200)

    def test_transfer_negative_amount(self):
        with self.assertRaises(BalanceException):
            self.child_account.transfer_to_parent(-100)
        self.assertEqual(self.child_account.balance, 500)
        self.assertEqual(self.parent_account.balance, 1000)


    #
    # def test_transfer_to_self(self):
    #     # with self.assertRaises(BalanceException):
    #     self.child_account.transfer_to_parent(100, self.child_account)
    #     self.assertEqual(self.child_account.balance, 500)
    #     self.assertEqual(self.parent_account.balance, 1000)

class TestBankAccountClosure(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(0, 'TestAccount', min_balance=100)

    def test_close_account_with_zero_balance(self):
        self.account.balance=0
        self.account.close_account()
        self.assertTrue(self.account.is_blocked)
        self.assertEqual(len(self.account.transaction_history), 2)
        self.assertEqual(self.account.transaction_history[1][0], 'Account Closed')
        self.assertEqual(self.account.transaction_history[1][1], 0)

    def test_close_account_with_positive_balance(self):
        self.account.deposit(200)  # Ensure positive balance
        self.account.close_account()
        self.assertTrue(self.account.is_blocked)
        self.assertEqual(len(self.account.transaction_history), 3)
        self.assertEqual(self.account.transaction_history[2][0], 'Account Closed')
        self.assertEqual(self.account.transaction_history[2][1], 0)

    def test_close_account_with_balance_below_min(self):
        self.account.withdraw(950)  # Bring balance below min_balance
        # with self.assertRaises(BalanceException):
        self.account.close_account()
        self.assertTrue(self.account.is_blocked)  # Should not be blocked
        self.assertEqual(len(self.account.transaction_history), 2)  # No closure transaction

    def test_close_blocked_account(self):
        self.account.withdraw(950)  # Block the account
        self.account.close_account()
        self.assertTrue(self.account.is_blocked)
        self.assertEqual(len(self.account.transaction_history), 2)
        self.assertEqual(self.account.transaction_history[0][0], 'Account Closed')
        self.assertEqual(self.account.transaction_history[0][1], 0)

if __name__ == '__main__':
    unittest.main()
