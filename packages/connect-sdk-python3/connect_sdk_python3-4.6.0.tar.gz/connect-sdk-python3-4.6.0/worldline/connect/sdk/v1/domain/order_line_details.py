# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class OrderLineDetails(DataObject):

    __discount_amount: Optional[int] = None
    __google_product_category_id: Optional[int] = None
    __line_amount_total: Optional[int] = None
    __naics_commodity_code: Optional[str] = None
    __product_category: Optional[str] = None
    __product_code: Optional[str] = None
    __product_image_url: Optional[str] = None
    __product_name: Optional[str] = None
    __product_price: Optional[int] = None
    __product_sku: Optional[str] = None
    __product_type: Optional[str] = None
    __product_url: Optional[str] = None
    __quantity: Optional[int] = None
    __tax_amount: Optional[int] = None
    __unit: Optional[str] = None

    @property
    def discount_amount(self) -> Optional[int]:
        """
        | Discount on the line item, with the last two digits implied as decimal places

        Type: int
        """
        return self.__discount_amount

    @discount_amount.setter
    def discount_amount(self, value: Optional[int]) -> None:
        self.__discount_amount = value

    @property
    def google_product_category_id(self) -> Optional[int]:
        """
        | The Google product category ID for the item.

        Type: int
        """
        return self.__google_product_category_id

    @google_product_category_id.setter
    def google_product_category_id(self, value: Optional[int]) -> None:
        self.__google_product_category_id = value

    @property
    def line_amount_total(self) -> Optional[int]:
        """
        | Total amount for the line item

        Type: int
        """
        return self.__line_amount_total

    @line_amount_total.setter
    def line_amount_total(self, value: Optional[int]) -> None:
        self.__line_amount_total = value

    @property
    def naics_commodity_code(self) -> Optional[str]:
        """
        | The UNSPC commodity code of the item.

        Type: str
        """
        return self.__naics_commodity_code

    @naics_commodity_code.setter
    def naics_commodity_code(self, value: Optional[str]) -> None:
        self.__naics_commodity_code = value

    @property
    def product_category(self) -> Optional[str]:
        """
        | The category of the product (i.e. home appliance). This property can be used for fraud screening on the Ogone Platform.

        Type: str
        """
        return self.__product_category

    @product_category.setter
    def product_category(self, value: Optional[str]) -> None:
        self.__product_category = value

    @property
    def product_code(self) -> Optional[str]:
        """
        | Product or UPC Code, left justified
        | Note: Must not be all spaces or all zeros

        Type: str
        """
        return self.__product_code

    @product_code.setter
    def product_code(self, value: Optional[str]) -> None:
        self.__product_code = value

    @property
    def product_image_url(self) -> Optional[str]:
        """
        | The URL of the image of the purchased product.

        Type: str
        """
        return self.__product_image_url

    @product_image_url.setter
    def product_image_url(self, value: Optional[str]) -> None:
        self.__product_image_url = value

    @property
    def product_name(self) -> Optional[str]:
        """
        | The name of the product. The '+' character is not allowed in this property for transactions that are processed by TechProcess Payment Platform.

        Type: str
        """
        return self.__product_name

    @product_name.setter
    def product_name(self, value: Optional[str]) -> None:
        self.__product_name = value

    @property
    def product_price(self) -> Optional[int]:
        """
        | The price of one unit of the product, the value should be zero or greater

        Type: int
        """
        return self.__product_price

    @product_price.setter
    def product_price(self, value: Optional[int]) -> None:
        self.__product_price = value

    @property
    def product_sku(self) -> Optional[str]:
        """
        | Product SKU number

        Type: str
        """
        return self.__product_sku

    @product_sku.setter
    def product_sku(self, value: Optional[str]) -> None:
        self.__product_sku = value

    @property
    def product_type(self) -> Optional[str]:
        """
        | Code used to classify items that are purchased
        | Note: Must not be all spaces or all zeros

        Type: str
        """
        return self.__product_type

    @product_type.setter
    def product_type(self, value: Optional[str]) -> None:
        self.__product_type = value

    @property
    def product_url(self) -> Optional[str]:
        """
        | The URL of the product page on your website.

        Type: str
        """
        return self.__product_url

    @product_url.setter
    def product_url(self, value: Optional[str]) -> None:
        self.__product_url = value

    @property
    def quantity(self) -> Optional[int]:
        """
        | Quantity of the units being purchased, should be greater than zero
        | Note: Must not be all spaces or all zeros

        Type: int
        """
        return self.__quantity

    @quantity.setter
    def quantity(self, value: Optional[int]) -> None:
        self.__quantity = value

    @property
    def tax_amount(self) -> Optional[int]:
        """
        | Tax on the line item, with the last two digits implied as decimal places

        Type: int
        """
        return self.__tax_amount

    @tax_amount.setter
    def tax_amount(self, value: Optional[int]) -> None:
        self.__tax_amount = value

    @property
    def unit(self) -> Optional[str]:
        """
        | Indicates the line item unit of measure; for example: each, kit, pair, gallon, month, etc.

        Type: str
        """
        return self.__unit

    @unit.setter
    def unit(self, value: Optional[str]) -> None:
        self.__unit = value

    def to_dictionary(self) -> dict:
        dictionary = super(OrderLineDetails, self).to_dictionary()
        if self.discount_amount is not None:
            dictionary['discountAmount'] = self.discount_amount
        if self.google_product_category_id is not None:
            dictionary['googleProductCategoryId'] = self.google_product_category_id
        if self.line_amount_total is not None:
            dictionary['lineAmountTotal'] = self.line_amount_total
        if self.naics_commodity_code is not None:
            dictionary['naicsCommodityCode'] = self.naics_commodity_code
        if self.product_category is not None:
            dictionary['productCategory'] = self.product_category
        if self.product_code is not None:
            dictionary['productCode'] = self.product_code
        if self.product_image_url is not None:
            dictionary['productImageUrl'] = self.product_image_url
        if self.product_name is not None:
            dictionary['productName'] = self.product_name
        if self.product_price is not None:
            dictionary['productPrice'] = self.product_price
        if self.product_sku is not None:
            dictionary['productSku'] = self.product_sku
        if self.product_type is not None:
            dictionary['productType'] = self.product_type
        if self.product_url is not None:
            dictionary['productUrl'] = self.product_url
        if self.quantity is not None:
            dictionary['quantity'] = self.quantity
        if self.tax_amount is not None:
            dictionary['taxAmount'] = self.tax_amount
        if self.unit is not None:
            dictionary['unit'] = self.unit
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'OrderLineDetails':
        super(OrderLineDetails, self).from_dictionary(dictionary)
        if 'discountAmount' in dictionary:
            self.discount_amount = dictionary['discountAmount']
        if 'googleProductCategoryId' in dictionary:
            self.google_product_category_id = dictionary['googleProductCategoryId']
        if 'lineAmountTotal' in dictionary:
            self.line_amount_total = dictionary['lineAmountTotal']
        if 'naicsCommodityCode' in dictionary:
            self.naics_commodity_code = dictionary['naicsCommodityCode']
        if 'productCategory' in dictionary:
            self.product_category = dictionary['productCategory']
        if 'productCode' in dictionary:
            self.product_code = dictionary['productCode']
        if 'productImageUrl' in dictionary:
            self.product_image_url = dictionary['productImageUrl']
        if 'productName' in dictionary:
            self.product_name = dictionary['productName']
        if 'productPrice' in dictionary:
            self.product_price = dictionary['productPrice']
        if 'productSku' in dictionary:
            self.product_sku = dictionary['productSku']
        if 'productType' in dictionary:
            self.product_type = dictionary['productType']
        if 'productUrl' in dictionary:
            self.product_url = dictionary['productUrl']
        if 'quantity' in dictionary:
            self.quantity = dictionary['quantity']
        if 'taxAmount' in dictionary:
            self.tax_amount = dictionary['taxAmount']
        if 'unit' in dictionary:
            self.unit = dictionary['unit']
        return self
