import asyncio
from datetime import  datetime
from .mappers import ContextRequest , env_variables
from . import service
import os

from .service import DB
class concept_sentinel_data_capturer:
    flag_env_variables = False
    @staticmethod
    def insertion_with_context(payload: ContextRequest):
        if not concept_sentinel_data_capturer.flag_env_variables:
            raise RuntimeError("Environment variables must be set using set_env_variables() before using this function")
        try:
            start_time = datetime.now()
            print(f"start_time: {start_time}")
            print("before invoking records_insertion service ")
            response = asyncio.run(service.insertion_with_context(payload))
            print("after invoking records_insertion service ")
            print("exit create usecase routing method")
            end_time = datetime.now()
            print(f"end_time: {end_time}")
            total_time = end_time - start_time
            print(f"total_time: {total_time}")  

            return response
        except Exception as e:
            print(e)
            raise

    @staticmethod
    def set_env_variables(env_vars: env_variables)-> None:
        """
        Validate the environment variables against the defined schema.And setup environment variables.
        
        Args:
            env_vars (env_variables): An instance of env_variables containing the environment variables.
        """
        try:
            for key, value in env_vars.model_dump().items():
                os.environ[key] = value
            concept_sentinel_data_capturer.flag_env_variables = True
            print("Environment variables set successfully.")
        except Exception as e:
            print(f"Validation error: {e}")