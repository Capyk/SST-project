import unittest
from bank_accounts import BankAccount, InterestRewardsAcct, SavingsAcct, BalanceException

class TestBankAccount(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(1000, 'TestAccount')

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, 1000)

    def test_deposit(self):
        self.account.deposit(500)
        self.assertEqual(self.account.balance, 1500)

    def test_withdraw(self):
        self.account.withdraw(200)
        self.assertEqual(self.account.balance, 800)

    def test_withdraw_insufficient_balance(self):
        with self.assertRaises(BalanceException):
            self.account.withdraw(1500)

    def test_transfer(self):
        other_account = BankAccount(500, 'OtherAccount')
        self.account.transfer(300, other_account)
        self.assertEqual(self.account.balance, 700)
        self.assertEqual(other_account.balance, 800)

class TestInterestRewardsAcct(unittest.TestCase):

    def setUp(self):
        self.account = InterestRewardsAcct(1000, 'InterestAccount')

    def test_deposit_interest(self):
        self.account.deposit(100)
        self.assertEqual(self.account.balance, 1105)  # 1000 + 100 * 1.05

class TestSavingsAcct(unittest.TestCase):

    def setUp(self):
        self.account = SavingsAcct(1000, 'SavingsAccount')

    def test_withdraw_with_fee(self):
        self.account.withdraw(100)  # 100 + 5 fee
        self.assertEqual(self.account.balance, 895)  # 1000 - 105

# Continue from the previous tests...

class TestBankAccountExtended(unittest.TestCase):

    def setUp(self):
        self.account = BankAccount(1000, 'ExtendedTestAccount')

    def test_negative_deposit(self):
        with self.assertRaises(BalanceException):
            self.account.deposit(-100)

    def test_large_withdrawal(self):
        self.account.withdraw(1000)
        self.assertEqual(self.account.balance, 0)

    def test_invalid_transfer_amount(self):
        other_account = BankAccount(500, 'OtherAccount2')
        with self.assertRaises(BalanceException):
            self.account.transfer(-100, other_account)

    def test_transfer_to_self(self):
        with self.assertRaises(BalanceException):
            self.account.transfer(100, self.account)

class TestInterestRewardsAcctExtended(unittest.TestCase):

    def setUp(self):
        self.account = InterestRewardsAcct(1000, 'ExtendedInterestAccount')

    def test_interest_on_negative_deposit(self):
        with self.assertRaises(BalanceException):
            self.account.deposit(-100)

class TestSavingsAcctExtended(unittest.TestCase):

    def setUp(self):
        self.account = SavingsAcct(100, 'ExtendedSavingsAccount')

    def test_withdrawal_fee_exceeding_balance(self):
        with self.assertRaises(BalanceException):
            self.account.withdraw(95)

    def test_initial_balance_with_fee(self):
        self.account = SavingsAcct(105, 'LowBalanceSavingsAccount')
        self.account.withdraw(100)
        self.assertEqual(self.account.balance, 0)

if __name__ == '__main__':
    unittest.main()

