# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.bank_transfer_payment_method_specific_output import BankTransferPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.card_payment_method_specific_output import CardPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.cash_payment_method_specific_output import CashPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.e_invoice_payment_method_specific_output import EInvoicePaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.invoice_payment_method_specific_output import InvoicePaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.mobile_payment_method_specific_output import MobilePaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_method_specific_output import NonSepaDirectDebitPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.order_output import OrderOutput
from worldline.connect.sdk.v1.domain.redirect_payment_method_specific_output import RedirectPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_method_specific_output import SepaDirectDebitPaymentMethodSpecificOutput


class PaymentOutput(OrderOutput):

    __amount_paid: Optional[int] = None
    __amount_reversed: Optional[int] = None
    __bank_transfer_payment_method_specific_output: Optional[BankTransferPaymentMethodSpecificOutput] = None
    __card_payment_method_specific_output: Optional[CardPaymentMethodSpecificOutput] = None
    __cash_payment_method_specific_output: Optional[CashPaymentMethodSpecificOutput] = None
    __direct_debit_payment_method_specific_output: Optional[NonSepaDirectDebitPaymentMethodSpecificOutput] = None
    __e_invoice_payment_method_specific_output: Optional[EInvoicePaymentMethodSpecificOutput] = None
    __invoice_payment_method_specific_output: Optional[InvoicePaymentMethodSpecificOutput] = None
    __mobile_payment_method_specific_output: Optional[MobilePaymentMethodSpecificOutput] = None
    __payment_method: Optional[str] = None
    __redirect_payment_method_specific_output: Optional[RedirectPaymentMethodSpecificOutput] = None
    __reversal_reason: Optional[str] = None
    __sepa_direct_debit_payment_method_specific_output: Optional[SepaDirectDebitPaymentMethodSpecificOutput] = None

    @property
    def amount_paid(self) -> Optional[int]:
        """
        | Amount that has been paid

        Type: int
        """
        return self.__amount_paid

    @amount_paid.setter
    def amount_paid(self, value: Optional[int]) -> None:
        self.__amount_paid = value

    @property
    def amount_reversed(self) -> Optional[int]:
        """
        | Amount that has been reversed

        Type: int
        """
        return self.__amount_reversed

    @amount_reversed.setter
    def amount_reversed(self, value: Optional[int]) -> None:
        self.__amount_reversed = value

    @property
    def bank_transfer_payment_method_specific_output(self) -> Optional[BankTransferPaymentMethodSpecificOutput]:
        """
        | Object containing the bank transfer payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.bank_transfer_payment_method_specific_output.BankTransferPaymentMethodSpecificOutput`
        """
        return self.__bank_transfer_payment_method_specific_output

    @bank_transfer_payment_method_specific_output.setter
    def bank_transfer_payment_method_specific_output(self, value: Optional[BankTransferPaymentMethodSpecificOutput]) -> None:
        self.__bank_transfer_payment_method_specific_output = value

    @property
    def card_payment_method_specific_output(self) -> Optional[CardPaymentMethodSpecificOutput]:
        """
        | Object containing the card payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.card_payment_method_specific_output.CardPaymentMethodSpecificOutput`
        """
        return self.__card_payment_method_specific_output

    @card_payment_method_specific_output.setter
    def card_payment_method_specific_output(self, value: Optional[CardPaymentMethodSpecificOutput]) -> None:
        self.__card_payment_method_specific_output = value

    @property
    def cash_payment_method_specific_output(self) -> Optional[CashPaymentMethodSpecificOutput]:
        """
        | Object containing the cash payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.cash_payment_method_specific_output.CashPaymentMethodSpecificOutput`
        """
        return self.__cash_payment_method_specific_output

    @cash_payment_method_specific_output.setter
    def cash_payment_method_specific_output(self, value: Optional[CashPaymentMethodSpecificOutput]) -> None:
        self.__cash_payment_method_specific_output = value

    @property
    def direct_debit_payment_method_specific_output(self) -> Optional[NonSepaDirectDebitPaymentMethodSpecificOutput]:
        """
        | Object containing the non SEPA direct debit payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_method_specific_output.NonSepaDirectDebitPaymentMethodSpecificOutput`
        """
        return self.__direct_debit_payment_method_specific_output

    @direct_debit_payment_method_specific_output.setter
    def direct_debit_payment_method_specific_output(self, value: Optional[NonSepaDirectDebitPaymentMethodSpecificOutput]) -> None:
        self.__direct_debit_payment_method_specific_output = value

    @property
    def e_invoice_payment_method_specific_output(self) -> Optional[EInvoicePaymentMethodSpecificOutput]:
        """
        | Object containing the e-invoice payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.e_invoice_payment_method_specific_output.EInvoicePaymentMethodSpecificOutput`
        """
        return self.__e_invoice_payment_method_specific_output

    @e_invoice_payment_method_specific_output.setter
    def e_invoice_payment_method_specific_output(self, value: Optional[EInvoicePaymentMethodSpecificOutput]) -> None:
        self.__e_invoice_payment_method_specific_output = value

    @property
    def invoice_payment_method_specific_output(self) -> Optional[InvoicePaymentMethodSpecificOutput]:
        """
        | Object containing the invoice payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.invoice_payment_method_specific_output.InvoicePaymentMethodSpecificOutput`
        """
        return self.__invoice_payment_method_specific_output

    @invoice_payment_method_specific_output.setter
    def invoice_payment_method_specific_output(self, value: Optional[InvoicePaymentMethodSpecificOutput]) -> None:
        self.__invoice_payment_method_specific_output = value

    @property
    def mobile_payment_method_specific_output(self) -> Optional[MobilePaymentMethodSpecificOutput]:
        """
        | Object containing the mobile payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.mobile_payment_method_specific_output.MobilePaymentMethodSpecificOutput`
        """
        return self.__mobile_payment_method_specific_output

    @mobile_payment_method_specific_output.setter
    def mobile_payment_method_specific_output(self, value: Optional[MobilePaymentMethodSpecificOutput]) -> None:
        self.__mobile_payment_method_specific_output = value

    @property
    def payment_method(self) -> Optional[str]:
        """
        | Payment method identifier used by the our payment engine with the following possible values:
        
        * bankRefund
        * bankTransfer
        * card
        * cash
        * directDebit
        * eInvoice
        * invoice
        * redirect

        Type: str
        """
        return self.__payment_method

    @payment_method.setter
    def payment_method(self, value: Optional[str]) -> None:
        self.__payment_method = value

    @property
    def redirect_payment_method_specific_output(self) -> Optional[RedirectPaymentMethodSpecificOutput]:
        """
        | Object containing the redirect payment product details

        Type: :class:`worldline.connect.sdk.v1.domain.redirect_payment_method_specific_output.RedirectPaymentMethodSpecificOutput`
        """
        return self.__redirect_payment_method_specific_output

    @redirect_payment_method_specific_output.setter
    def redirect_payment_method_specific_output(self, value: Optional[RedirectPaymentMethodSpecificOutput]) -> None:
        self.__redirect_payment_method_specific_output = value

    @property
    def reversal_reason(self) -> Optional[str]:
        """
        | The reason description given for the reversedAmount property.

        Type: str
        """
        return self.__reversal_reason

    @reversal_reason.setter
    def reversal_reason(self, value: Optional[str]) -> None:
        self.__reversal_reason = value

    @property
    def sepa_direct_debit_payment_method_specific_output(self) -> Optional[SepaDirectDebitPaymentMethodSpecificOutput]:
        """
        | Object containing the SEPA direct debit details

        Type: :class:`worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_method_specific_output.SepaDirectDebitPaymentMethodSpecificOutput`
        """
        return self.__sepa_direct_debit_payment_method_specific_output

    @sepa_direct_debit_payment_method_specific_output.setter
    def sepa_direct_debit_payment_method_specific_output(self, value: Optional[SepaDirectDebitPaymentMethodSpecificOutput]) -> None:
        self.__sepa_direct_debit_payment_method_specific_output = value

    def to_dictionary(self) -> dict:
        dictionary = super(PaymentOutput, self).to_dictionary()
        if self.amount_paid is not None:
            dictionary['amountPaid'] = self.amount_paid
        if self.amount_reversed is not None:
            dictionary['amountReversed'] = self.amount_reversed
        if self.bank_transfer_payment_method_specific_output is not None:
            dictionary['bankTransferPaymentMethodSpecificOutput'] = self.bank_transfer_payment_method_specific_output.to_dictionary()
        if self.card_payment_method_specific_output is not None:
            dictionary['cardPaymentMethodSpecificOutput'] = self.card_payment_method_specific_output.to_dictionary()
        if self.cash_payment_method_specific_output is not None:
            dictionary['cashPaymentMethodSpecificOutput'] = self.cash_payment_method_specific_output.to_dictionary()
        if self.direct_debit_payment_method_specific_output is not None:
            dictionary['directDebitPaymentMethodSpecificOutput'] = self.direct_debit_payment_method_specific_output.to_dictionary()
        if self.e_invoice_payment_method_specific_output is not None:
            dictionary['eInvoicePaymentMethodSpecificOutput'] = self.e_invoice_payment_method_specific_output.to_dictionary()
        if self.invoice_payment_method_specific_output is not None:
            dictionary['invoicePaymentMethodSpecificOutput'] = self.invoice_payment_method_specific_output.to_dictionary()
        if self.mobile_payment_method_specific_output is not None:
            dictionary['mobilePaymentMethodSpecificOutput'] = self.mobile_payment_method_specific_output.to_dictionary()
        if self.payment_method is not None:
            dictionary['paymentMethod'] = self.payment_method
        if self.redirect_payment_method_specific_output is not None:
            dictionary['redirectPaymentMethodSpecificOutput'] = self.redirect_payment_method_specific_output.to_dictionary()
        if self.reversal_reason is not None:
            dictionary['reversalReason'] = self.reversal_reason
        if self.sepa_direct_debit_payment_method_specific_output is not None:
            dictionary['sepaDirectDebitPaymentMethodSpecificOutput'] = self.sepa_direct_debit_payment_method_specific_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PaymentOutput':
        super(PaymentOutput, self).from_dictionary(dictionary)
        if 'amountPaid' in dictionary:
            self.amount_paid = dictionary['amountPaid']
        if 'amountReversed' in dictionary:
            self.amount_reversed = dictionary['amountReversed']
        if 'bankTransferPaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['bankTransferPaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankTransferPaymentMethodSpecificOutput']))
            value = BankTransferPaymentMethodSpecificOutput()
            self.bank_transfer_payment_method_specific_output = value.from_dictionary(dictionary['bankTransferPaymentMethodSpecificOutput'])
        if 'cardPaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['cardPaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['cardPaymentMethodSpecificOutput']))
            value = CardPaymentMethodSpecificOutput()
            self.card_payment_method_specific_output = value.from_dictionary(dictionary['cardPaymentMethodSpecificOutput'])
        if 'cashPaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['cashPaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['cashPaymentMethodSpecificOutput']))
            value = CashPaymentMethodSpecificOutput()
            self.cash_payment_method_specific_output = value.from_dictionary(dictionary['cashPaymentMethodSpecificOutput'])
        if 'directDebitPaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['directDebitPaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['directDebitPaymentMethodSpecificOutput']))
            value = NonSepaDirectDebitPaymentMethodSpecificOutput()
            self.direct_debit_payment_method_specific_output = value.from_dictionary(dictionary['directDebitPaymentMethodSpecificOutput'])
        if 'eInvoicePaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['eInvoicePaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['eInvoicePaymentMethodSpecificOutput']))
            value = EInvoicePaymentMethodSpecificOutput()
            self.e_invoice_payment_method_specific_output = value.from_dictionary(dictionary['eInvoicePaymentMethodSpecificOutput'])
        if 'invoicePaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['invoicePaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['invoicePaymentMethodSpecificOutput']))
            value = InvoicePaymentMethodSpecificOutput()
            self.invoice_payment_method_specific_output = value.from_dictionary(dictionary['invoicePaymentMethodSpecificOutput'])
        if 'mobilePaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['mobilePaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['mobilePaymentMethodSpecificOutput']))
            value = MobilePaymentMethodSpecificOutput()
            self.mobile_payment_method_specific_output = value.from_dictionary(dictionary['mobilePaymentMethodSpecificOutput'])
        if 'paymentMethod' in dictionary:
            self.payment_method = dictionary['paymentMethod']
        if 'redirectPaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['redirectPaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['redirectPaymentMethodSpecificOutput']))
            value = RedirectPaymentMethodSpecificOutput()
            self.redirect_payment_method_specific_output = value.from_dictionary(dictionary['redirectPaymentMethodSpecificOutput'])
        if 'reversalReason' in dictionary:
            self.reversal_reason = dictionary['reversalReason']
        if 'sepaDirectDebitPaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['sepaDirectDebitPaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['sepaDirectDebitPaymentMethodSpecificOutput']))
            value = SepaDirectDebitPaymentMethodSpecificOutput()
            self.sepa_direct_debit_payment_method_specific_output = value.from_dictionary(dictionary['sepaDirectDebitPaymentMethodSpecificOutput'])
        return self
