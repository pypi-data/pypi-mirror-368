# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class OrderTypeInformation(DataObject):

    __funding_type: Optional[str] = None
    __payment_code: Optional[str] = None
    __purchase_type: Optional[str] = None
    __transaction_type: Optional[str] = None
    __usage_type: Optional[str] = None

    @property
    def funding_type(self) -> Optional[str]:
        """
        | Identifies the funding type being authenticated. Possible values are:
        
        * personToPerson = When it is person to person funding (P2P)
        * agentCashOut = When fund is being paid out to final recipient in Cash by company's agent.
        * businessToConsumer = When fund is being transferred from business to consumer (B2C)
        * businessToBusiness = When fund is being transferred from business to business (B2B)
        * prefundingStagedWallet = When funding is being used to load the funds into the wallet account.
        * storedValueDigitalWallet = When funding is being used to load the funds into a stored value digital wallet.
        * fundingGiftCardForPersonalUse = When funding a gift card for personal use.
        * fundingGiftCardForSomeoneElse = When funding a gift card for someone else.

        Type: str
        """
        return self.__funding_type

    @funding_type.setter
    def funding_type(self, value: Optional[str]) -> None:
        self.__funding_type = value

    @property
    def payment_code(self) -> Optional[str]:
        """
        | Payment code to support account funding transactions. Possible values are:
        
        * accountManagement
        * paymentAllowance
        * settlementOfAnnuity
        * unemploymentDisabilityBenefit
        * businessExpenses
        * bonusPayment
        * busTransportRelatedBusiness
        * cashManagementTransfer
        * paymentOfCableTVBill
        * governmentInstituteIssued
        * creditCardPayment
        * creditCardBill
        * charity
        * collectionPayment
        * commercialPayment
        * commission
        * compensation
        * copyright
        * debitCardPayment
        * deposit
        * dividend
        * studyFees
        * electricityBill
        * energies
        * generalFees
        * ferry
        * foreignExchange
        * gasBill
        * unemployedCompensation
        * governmentPayment
        * healthInsurance
        * reimbursementCreditCard
        * reimbursementDebitCard
        * carInsurancePremium
        * insuranceClaim
        * installment
        * insurancePremium
        * investmentPayment
        * intraCompany
        * interest
        * incomeTax
        * investment
        * laborInsurance
        * licenseFree
        * lifeInsurance
        * loan
        * medicalServices
        * mobilePersonToBusiness
        * mobilePersonToPerson
        * mobileTopUp
        * notSpecified
        * other
        * anotherTelecomBill
        * payroll
        * pensionFundContribution
        * pensionPayment
        * telephoneBill
        * propertyInsurance
        * generalLease
        * rent
        * railwayPayment
        * royalties
        * salary
        * savingsPayment
        * securities
        * socialSecurity
        * study
        * subscription
        * supplierPayment
        * taxRefund
        * taxPayment
        * telecommunicationsBill
        * tradeServices
        * treasuryPayment
        * travelPayment
        * utilityBill
        * valueAddedTaxPayment
        * withHolding
        * waterBill
        
        | .

        Type: str
        """
        return self.__payment_code

    @payment_code.setter
    def payment_code(self, value: Optional[str]) -> None:
        self.__payment_code = value

    @property
    def purchase_type(self) -> Optional[str]:
        """
        | Possible values are:
        
        * physical
        * digital

        Type: str
        """
        return self.__purchase_type

    @purchase_type.setter
    def purchase_type(self, value: Optional[str]) -> None:
        self.__purchase_type = value

    @property
    def transaction_type(self) -> Optional[str]:
        """
        | Identifies the type of transaction being authenticated.Possible values are:
        
        * purchase = The purpose of the transaction is to purchase goods or services (Default)
        * check-acceptance = The purpose of the transaction is to accept a 'check'/'cheque'
        * account-funding = The purpose of the transaction is to fund an account
        * quasi-cash = The purpose of the transaction is to buy a quasi cash type product that is representative of actual cash such as money orders, traveler's checks, foreign currency, lottery tickets or casino gaming chips
        * prepaid-activation-or-load = The purpose of the transaction is to activate or load a prepaid card

        Type: str
        """
        return self.__transaction_type

    @transaction_type.setter
    def transaction_type(self, value: Optional[str]) -> None:
        self.__transaction_type = value

    @property
    def usage_type(self) -> Optional[str]:
        """
        | Possible values are:
        
        * private
        * commercial

        Type: str
        """
        return self.__usage_type

    @usage_type.setter
    def usage_type(self, value: Optional[str]) -> None:
        self.__usage_type = value

    def to_dictionary(self) -> dict:
        dictionary = super(OrderTypeInformation, self).to_dictionary()
        if self.funding_type is not None:
            dictionary['fundingType'] = self.funding_type
        if self.payment_code is not None:
            dictionary['paymentCode'] = self.payment_code
        if self.purchase_type is not None:
            dictionary['purchaseType'] = self.purchase_type
        if self.transaction_type is not None:
            dictionary['transactionType'] = self.transaction_type
        if self.usage_type is not None:
            dictionary['usageType'] = self.usage_type
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'OrderTypeInformation':
        super(OrderTypeInformation, self).from_dictionary(dictionary)
        if 'fundingType' in dictionary:
            self.funding_type = dictionary['fundingType']
        if 'paymentCode' in dictionary:
            self.payment_code = dictionary['paymentCode']
        if 'purchaseType' in dictionary:
            self.purchase_type = dictionary['purchaseType']
        if 'transactionType' in dictionary:
            self.transaction_type = dictionary['transactionType']
        if 'usageType' in dictionary:
            self.usage_type = dictionary['usageType']
        return self
