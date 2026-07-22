import uuid
import secrets


class APIKeyEngine:
    def get_uuid(self) -> uuid.UUID:
        return str(uuid.uuid4())

    def get_prefix(self):
        return "monitora"

    def get_suffix(self) -> str:
        return "za"

    def get_numeric(self) -> str:
        return str(secrets.SystemRandom().randint(1000000, 9999999))

    def generate_key(self):
        pass

    def split_by_point(self, *args) -> str:
        splited_key = ""
        for _ in args:
            splited_key += " " + _
        cleaned_key_splited = splited_key.strip().split()
        join_key = "_".join(cleaned_key_splited).upper()
        return join_key

    def generate_basic_key(self) -> str:
        return self.split_by_point(
            self.get_prefix(), self.get_uuid(), self.get_numeric(), self.get_suffix()
        )

    def validator(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("Invalid Key: key is None")

        if "_" not in api_key:
            raise ValueError("Invalid Key: key has no separater.")

        if api_key.count("_") != 3:
            raise ValueError("Invalid Key: invalid total '_' counted")

        splited_key = api_key.split("_")

        count_elements = 0
        for element in splited_key:
            if not element or element == "":
                raise ValueError("Invalid Key: one of the element is empty")
            count_elements += 1

        if count_elements != 4:
            raise ValueError("Invalid Key: invalid key length.")

        if splited_key[0] != self.get_prefix().upper():
            raise ValueError("Invalid Key: invalid prefix")

        try:
            uuid.UUID(str(splited_key[1]).lower())
        except Exception as e:
            raise ValueError(f"Invalid Key: invalid UUID {e}")

        str_splited_key = str(splited_key[2])
        if not str_splited_key.isnumeric() or len(str_splited_key) != 7:
            raise ValueError("Invalid Key: invalid numeric")

        if splited_key[-1] != self.get_suffix().upper():
            raise ValueError("Invalid Key: suffix not valid")

    def is_valid(self, api_key: str) -> bool:
        try:
            self.validator(api_key)
            return True
        except Exception:
            return False
