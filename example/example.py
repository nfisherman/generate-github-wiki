class test1:
    """
    Some info.
    """

    def someFunction(num: int, string: str, num_list: list[int]) -> bool:
        """
        A function.

        Args:
            num (int): A number.
            string (str): A string.
            num_list (int): A list of numbers.

        Returns:
            bool: True
        """
        return True
    
    def someOtherFunction(string: str, num_list: list[int], num: int) -> bool:
        """
        Another function.

        Args:
            string (str): A string.
            num_list (int): A list of numbers.
            num (int): A number.

        Returns:
            bool: False
        """
        return False

    def __privateFunction() -> int:
        """
        A private function.

        Returns:
            int: the result of 2+2
        """
        return 2+2

class test2:
    """
    Some other info.
    """

    def throwSomeException() -> Exception:
        """
        A function that throws an exception.

        Returns:
            Exception: An Exception.
        """
        return Exception()
