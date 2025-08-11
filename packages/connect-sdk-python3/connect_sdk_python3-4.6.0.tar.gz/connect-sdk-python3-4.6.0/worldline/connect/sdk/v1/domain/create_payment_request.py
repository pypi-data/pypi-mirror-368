# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.bank_transfer_payment_method_specific_input import BankTransferPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.card_payment_method_specific_input import CardPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.cash_payment_method_specific_input import CashPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.e_invoice_payment_method_specific_input import EInvoicePaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.fraud_fields import FraudFields
from worldline.connect.sdk.v1.domain.invoice_payment_method_specific_input import InvoicePaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.merchant import Merchant
from worldline.connect.sdk.v1.domain.mobile_payment_method_specific_input import MobilePaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_method_specific_input import NonSepaDirectDebitPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.order import Order
from worldline.connect.sdk.v1.domain.redirect_payment_method_specific_input import RedirectPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_method_specific_input import SepaDirectDebitPaymentMethodSpecificInput


class CreatePaymentRequest(DataObject):

    __bank_transfer_payment_method_specific_input: Optional[BankTransferPaymentMethodSpecificInput] = None
    __card_payment_method_specific_input: Optional[CardPaymentMethodSpecificInput] = None
    __cash_payment_method_specific_input: Optional[CashPaymentMethodSpecificInput] = None
    __direct_debit_payment_method_specific_input: Optional[NonSepaDirectDebitPaymentMethodSpecificInput] = None
    __e_invoice_payment_method_specific_input: Optional[EInvoicePaymentMethodSpecificInput] = None
    __encrypted_customer_input: Optional[str] = None
    __fraud_fields: Optional[FraudFields] = None
    __invoice_payment_method_specific_input: Optional[InvoicePaymentMethodSpecificInput] = None
    __merchant: Optional[Merchant] = None
    __mobile_payment_method_specific_input: Optional[MobilePaymentMethodSpecificInput] = None
    __order: Optional[Order] = None
    __redirect_payment_method_specific_input: Optional[RedirectPaymentMethodSpecificInput] = None
    __sepa_direct_debit_payment_method_specific_input: Optional[SepaDirectDebitPaymentMethodSpecificInput] = None

    @property
    def bank_transfer_payment_method_specific_input(self) -> Optional[BankTransferPaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for bank transfer payments

        Type: :class:`worldline.connect.sdk.v1.domain.bank_transfer_payment_method_specific_input.BankTransferPaymentMethodSpecificInput`
        """
        return self.__bank_transfer_payment_method_specific_input

    @bank_transfer_payment_method_specific_input.setter
    def bank_transfer_payment_method_specific_input(self, value: Optional[BankTransferPaymentMethodSpecificInput]) -> None:
        self.__bank_transfer_payment_method_specific_input = value

    @property
    def card_payment_method_specific_input(self) -> Optional[CardPaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for card payments

        Type: :class:`worldline.connect.sdk.v1.domain.card_payment_method_specific_input.CardPaymentMethodSpecificInput`
        """
        return self.__card_payment_method_specific_input

    @card_payment_method_specific_input.setter
    def card_payment_method_specific_input(self, value: Optional[CardPaymentMethodSpecificInput]) -> None:
        self.__card_payment_method_specific_input = value

    @property
    def cash_payment_method_specific_input(self) -> Optional[CashPaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for cash payments

        Type: :class:`worldline.connect.sdk.v1.domain.cash_payment_method_specific_input.CashPaymentMethodSpecificInput`
        """
        return self.__cash_payment_method_specific_input

    @cash_payment_method_specific_input.setter
    def cash_payment_method_specific_input(self, value: Optional[CashPaymentMethodSpecificInput]) -> None:
        self.__cash_payment_method_specific_input = value

    @property
    def direct_debit_payment_method_specific_input(self) -> Optional[NonSepaDirectDebitPaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for direct debit payments

        Type: :class:`worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_method_specific_input.NonSepaDirectDebitPaymentMethodSpecificInput`
        """
        return self.__direct_debit_payment_method_specific_input

    @direct_debit_payment_method_specific_input.setter
    def direct_debit_payment_method_specific_input(self, value: Optional[NonSepaDirectDebitPaymentMethodSpecificInput]) -> None:
        self.__direct_debit_payment_method_specific_input = value

    @property
    def e_invoice_payment_method_specific_input(self) -> Optional[EInvoicePaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for e-invoice payments.

        Type: :class:`worldline.connect.sdk.v1.domain.e_invoice_payment_method_specific_input.EInvoicePaymentMethodSpecificInput`
        """
        return self.__e_invoice_payment_method_specific_input

    @e_invoice_payment_method_specific_input.setter
    def e_invoice_payment_method_specific_input(self, value: Optional[EInvoicePaymentMethodSpecificInput]) -> None:
        self.__e_invoice_payment_method_specific_input = value

    @property
    def encrypted_customer_input(self) -> Optional[str]:
        """
        | Data that was encrypted client side containing all customer entered data elements like card data.
        | Note: Because this data can only be submitted once to our system and contains encrypted card data you should not store it. As the data was captured within the context of a client session you also need to submit it to us before the session has expired.

        Type: str
        """
        return self.__encrypted_customer_input

    @encrypted_customer_input.setter
    def encrypted_customer_input(self, value: Optional[str]) -> None:
        self.__encrypted_customer_input = value

    @property
    def fraud_fields(self) -> Optional[FraudFields]:
        """
        | Object containing additional data that will be used to assess the risk of fraud

        Type: :class:`worldline.connect.sdk.v1.domain.fraud_fields.FraudFields`
        """
        return self.__fraud_fields

    @fraud_fields.setter
    def fraud_fields(self, value: Optional[FraudFields]) -> None:
        self.__fraud_fields = value

    @property
    def invoice_payment_method_specific_input(self) -> Optional[InvoicePaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for invoice payments

        Type: :class:`worldline.connect.sdk.v1.domain.invoice_payment_method_specific_input.InvoicePaymentMethodSpecificInput`
        """
        return self.__invoice_payment_method_specific_input

    @invoice_payment_method_specific_input.setter
    def invoice_payment_method_specific_input(self, value: Optional[InvoicePaymentMethodSpecificInput]) -> None:
        self.__invoice_payment_method_specific_input = value

    @property
    def merchant(self) -> Optional[Merchant]:
        """
        | Object containing information on you, the merchant

        Type: :class:`worldline.connect.sdk.v1.domain.merchant.Merchant`
        """
        return self.__merchant

    @merchant.setter
    def merchant(self, value: Optional[Merchant]) -> None:
        self.__merchant = value

    @property
    def mobile_payment_method_specific_input(self) -> Optional[MobilePaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for mobile payments.
        
        | Mobile payments produce the required payment data in encrypted form.
        
        * For Apple Pay, the encrypted payment data is the PKPayment <https://developer.apple.com/documentation/passkit/pkpayment>.token.paymentData object passed as a string (with all quotation marks escaped).
        * For Google Pay, the encrypted payment data can be found in property paymentMethodData.tokenizationData.token of the PaymentData <https://developers.google.com/android/reference/com/google/android/gms/wallet/PaymentData>.toJson() result.

        Type: :class:`worldline.connect.sdk.v1.domain.mobile_payment_method_specific_input.MobilePaymentMethodSpecificInput`
        """
        return self.__mobile_payment_method_specific_input

    @mobile_payment_method_specific_input.setter
    def mobile_payment_method_specific_input(self, value: Optional[MobilePaymentMethodSpecificInput]) -> None:
        self.__mobile_payment_method_specific_input = value

    @property
    def order(self) -> Optional[Order]:
        """
        | Order object containing order related data
        | Please note that this object is required to be able to submit the amount.

        Type: :class:`worldline.connect.sdk.v1.domain.order.Order`
        """
        return self.__order

    @order.setter
    def order(self, value: Optional[Order]) -> None:
        self.__order = value

    @property
    def redirect_payment_method_specific_input(self) -> Optional[RedirectPaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for payments that involve redirects to 3rd parties to complete, like iDeal and PayPal

        Type: :class:`worldline.connect.sdk.v1.domain.redirect_payment_method_specific_input.RedirectPaymentMethodSpecificInput`
        """
        return self.__redirect_payment_method_specific_input

    @redirect_payment_method_specific_input.setter
    def redirect_payment_method_specific_input(self, value: Optional[RedirectPaymentMethodSpecificInput]) -> None:
        self.__redirect_payment_method_specific_input = value

    @property
    def sepa_direct_debit_payment_method_specific_input(self) -> Optional[SepaDirectDebitPaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for SEPA direct debit payments

        Type: :class:`worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_method_specific_input.SepaDirectDebitPaymentMethodSpecificInput`
        """
        return self.__sepa_direct_debit_payment_method_specific_input

    @sepa_direct_debit_payment_method_specific_input.setter
    def sepa_direct_debit_payment_method_specific_input(self, value: Optional[SepaDirectDebitPaymentMethodSpecificInput]) -> None:
        self.__sepa_direct_debit_payment_method_specific_input = value

    def to_dictionary(self) -> dict:
        dictionary = super(CreatePaymentRequest, self).to_dictionary()
        if self.bank_transfer_payment_method_specific_input is not None:
            dictionary['bankTransferPaymentMethodSpecificInput'] = self.bank_transfer_payment_method_specific_input.to_dictionary()
        if self.card_payment_method_specific_input is not None:
            dictionary['cardPaymentMethodSpecificInput'] = self.card_payment_method_specific_input.to_dictionary()
        if self.cash_payment_method_specific_input is not None:
            dictionary['cashPaymentMethodSpecificInput'] = self.cash_payment_method_specific_input.to_dictionary()
        if self.direct_debit_payment_method_specific_input is not None:
            dictionary['directDebitPaymentMethodSpecificInput'] = self.direct_debit_payment_method_specific_input.to_dictionary()
        if self.e_invoice_payment_method_specific_input is not None:
            dictionary['eInvoicePaymentMethodSpecificInput'] = self.e_invoice_payment_method_specific_input.to_dictionary()
        if self.encrypted_customer_input is not None:
            dictionary['encryptedCustomerInput'] = self.encrypted_customer_input
        if self.fraud_fields is not None:
            dictionary['fraudFields'] = self.fraud_fields.to_dictionary()
        if self.invoice_payment_method_specific_input is not None:
            dictionary['invoicePaymentMethodSpecificInput'] = self.invoice_payment_method_specific_input.to_dictionary()
        if self.merchant is not None:
            dictionary['merchant'] = self.merchant.to_dictionary()
        if self.mobile_payment_method_specific_input is not None:
            dictionary['mobilePaymentMethodSpecificInput'] = self.mobile_payment_method_specific_input.to_dictionary()
        if self.order is not None:
            dictionary['order'] = self.order.to_dictionary()
        if self.redirect_payment_method_specific_input is not None:
            dictionary['redirectPaymentMethodSpecificInput'] = self.redirect_payment_method_specific_input.to_dictionary()
        if self.sepa_direct_debit_payment_method_specific_input is not None:
            dictionary['sepaDirectDebitPaymentMethodSpecificInput'] = self.sepa_direct_debit_payment_method_specific_input.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CreatePaymentRequest':
        super(CreatePaymentRequest, self).from_dictionary(dictionary)
        if 'bankTransferPaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['bankTransferPaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankTransferPaymentMethodSpecificInput']))
            value = BankTransferPaymentMethodSpecificInput()
            self.bank_transfer_payment_method_specific_input = value.from_dictionary(dictionary['bankTransferPaymentMethodSpecificInput'])
        if 'cardPaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['cardPaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['cardPaymentMethodSpecificInput']))
            value = CardPaymentMethodSpecificInput()
            self.card_payment_method_specific_input = value.from_dictionary(dictionary['cardPaymentMethodSpecificInput'])
        if 'cashPaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['cashPaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['cashPaymentMethodSpecificInput']))
            value = CashPaymentMethodSpecificInput()
            self.cash_payment_method_specific_input = value.from_dictionary(dictionary['cashPaymentMethodSpecificInput'])
        if 'directDebitPaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['directDebitPaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['directDebitPaymentMethodSpecificInput']))
            value = NonSepaDirectDebitPaymentMethodSpecificInput()
            self.direct_debit_payment_method_specific_input = value.from_dictionary(dictionary['directDebitPaymentMethodSpecificInput'])
        if 'eInvoicePaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['eInvoicePaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['eInvoicePaymentMethodSpecificInput']))
            value = EInvoicePaymentMethodSpecificInput()
            self.e_invoice_payment_method_specific_input = value.from_dictionary(dictionary['eInvoicePaymentMethodSpecificInput'])
        if 'encryptedCustomerInput' in dictionary:
            self.encrypted_customer_input = dictionary['encryptedCustomerInput']
        if 'fraudFields' in dictionary:
            if not isinstance(dictionary['fraudFields'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['fraudFields']))
            value = FraudFields()
            self.fraud_fields = value.from_dictionary(dictionary['fraudFields'])
        if 'invoicePaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['invoicePaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['invoicePaymentMethodSpecificInput']))
            value = InvoicePaymentMethodSpecificInput()
            self.invoice_payment_method_specific_input = value.from_dictionary(dictionary['invoicePaymentMethodSpecificInput'])
        if 'merchant' in dictionary:
            if not isinstance(dictionary['merchant'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['merchant']))
            value = Merchant()
            self.merchant = value.from_dictionary(dictionary['merchant'])
        if 'mobilePaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['mobilePaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['mobilePaymentMethodSpecificInput']))
            value = MobilePaymentMethodSpecificInput()
            self.mobile_payment_method_specific_input = value.from_dictionary(dictionary['mobilePaymentMethodSpecificInput'])
        if 'order' in dictionary:
            if not isinstance(dictionary['order'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['order']))
            value = Order()
            self.order = value.from_dictionary(dictionary['order'])
        if 'redirectPaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['redirectPaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['redirectPaymentMethodSpecificInput']))
            value = RedirectPaymentMethodSpecificInput()
            self.redirect_payment_method_specific_input = value.from_dictionary(dictionary['redirectPaymentMethodSpecificInput'])
        if 'sepaDirectDebitPaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['sepaDirectDebitPaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['sepaDirectDebitPaymentMethodSpecificInput']))
            value = SepaDirectDebitPaymentMethodSpecificInput()
            self.sepa_direct_debit_payment_method_specific_input = value.from_dictionary(dictionary['sepaDirectDebitPaymentMethodSpecificInput'])
        return self
