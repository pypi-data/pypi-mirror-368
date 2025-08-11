# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.bank_transfer_payment_method_specific_output import BankTransferPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.card_payment_method_specific_output import CardPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.cash_payment_method_specific_output import CashPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.order_output import OrderOutput
from worldline.connect.sdk.v1.domain.redirect_payment_method_specific_output import RedirectPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_method_specific_output import SepaDirectDebitPaymentMethodSpecificOutput


class CaptureOutput(OrderOutput):

    __amount_paid = None
    __amount_reversed = None
    __bank_transfer_payment_method_specific_output = None
    __card_payment_method_specific_output = None
    __cash_payment_method_specific_output = None
    __payment_method = None
    __redirect_payment_method_specific_output = None
    __reversal_reason = None
    __sepa_direct_debit_payment_method_specific_output = None

    @property
    def amount_paid(self):
        """
        | Amount that has been paid

        Type: long
        """
        return self.__amount_paid

    @amount_paid.setter
    def amount_paid(self, value):
        self.__amount_paid = value

    @property
    def amount_reversed(self):
        """
        | Amount that has been reversed

        Type: long
        """
        return self.__amount_reversed

    @amount_reversed.setter
    def amount_reversed(self, value):
        self.__amount_reversed = value

    @property
    def bank_transfer_payment_method_specific_output(self):
        """
        | Object containing the bank transfer payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.bank_transfer_payment_method_specific_output.BankTransferPaymentMethodSpecificOutput`
        """
        return self.__bank_transfer_payment_method_specific_output

    @bank_transfer_payment_method_specific_output.setter
    def bank_transfer_payment_method_specific_output(self, value):
        self.__bank_transfer_payment_method_specific_output = value

    @property
    def card_payment_method_specific_output(self):
        """
        | Object containing the card payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.card_payment_method_specific_output.CardPaymentMethodSpecificOutput`
        """
        return self.__card_payment_method_specific_output

    @card_payment_method_specific_output.setter
    def card_payment_method_specific_output(self, value):
        self.__card_payment_method_specific_output = value

    @property
    def cash_payment_method_specific_output(self):
        """
        | Object containing the cash payment method details

        Type: :class:`worldline.connect.sdk.v1.domain.cash_payment_method_specific_output.CashPaymentMethodSpecificOutput`
        """
        return self.__cash_payment_method_specific_output

    @cash_payment_method_specific_output.setter
    def cash_payment_method_specific_output(self, value):
        self.__cash_payment_method_specific_output = value

    @property
    def payment_method(self):
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
    def payment_method(self, value):
        self.__payment_method = value

    @property
    def redirect_payment_method_specific_output(self):
        """
        | Object containing the redirect payment product details

        Type: :class:`worldline.connect.sdk.v1.domain.redirect_payment_method_specific_output.RedirectPaymentMethodSpecificOutput`
        """
        return self.__redirect_payment_method_specific_output

    @redirect_payment_method_specific_output.setter
    def redirect_payment_method_specific_output(self, value):
        self.__redirect_payment_method_specific_output = value

    @property
    def reversal_reason(self):
        """
        | The reason description given for the reversedAmount property.

        Type: str
        """
        return self.__reversal_reason

    @reversal_reason.setter
    def reversal_reason(self, value):
        self.__reversal_reason = value

    @property
    def sepa_direct_debit_payment_method_specific_output(self):
        """
        | Object containing the SEPA direct debit details

        Type: :class:`worldline.connect.sdk.v1.domain.sepa_direct_debit_payment_method_specific_output.SepaDirectDebitPaymentMethodSpecificOutput`
        """
        return self.__sepa_direct_debit_payment_method_specific_output

    @sepa_direct_debit_payment_method_specific_output.setter
    def sepa_direct_debit_payment_method_specific_output(self, value):
        self.__sepa_direct_debit_payment_method_specific_output = value

    def to_dictionary(self):
        dictionary = super(CaptureOutput, self).to_dictionary()
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
        if self.payment_method is not None:
            dictionary['paymentMethod'] = self.payment_method
        if self.redirect_payment_method_specific_output is not None:
            dictionary['redirectPaymentMethodSpecificOutput'] = self.redirect_payment_method_specific_output.to_dictionary()
        if self.reversal_reason is not None:
            dictionary['reversalReason'] = self.reversal_reason
        if self.sepa_direct_debit_payment_method_specific_output is not None:
            dictionary['sepaDirectDebitPaymentMethodSpecificOutput'] = self.sepa_direct_debit_payment_method_specific_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary):
        super(CaptureOutput, self).from_dictionary(dictionary)
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
