import pytest
from usdpln_details import numbers_to_month


def test_numbers_to_month():
       result = numbers_to_month({'1': 122.362, '4': 126.558, '5': 126.15, '9': 129.271, '10': 130.599, '11': 127.903, '12': 131.766})
       assert result == {'January': 122.362, 'April': 126.558, 'May': 126.15, 'September': 129.271, 'October': 130.599, 'November': 127.903, 'December': 131.766}


def test_numbers_to_month_int():
       with pytest.raises(AttributeError):
              numbers_to_month(111)


def test_numbers_to_month_str():
       with pytest.raises(AttributeError):
              numbers_to_month("1111")


def test_numbers_to_month_list():
       with pytest.raises(AttributeError):
              numbers_to_month([1,2,3,43,54,5])

