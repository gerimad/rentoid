import openai
import os


class InferenceEngine():
    model="gpt-3.5-turbo"
    client = openai.OpenAI()
    api_key = os.getenv('OPENAI_API_KEY')
    pre_prompts = [
        {"role": "system", "content": "Act as a real estate salesman with 15+ years of experience with selling apartments in Budapest. Your task is to extract the most important information from apartment listings. "},
        {"role": "user", "content": 
        """The next message will be a real estate advert for an apartment for rent. Your answer must follow this format:
        Rent price: <rent price>

        Location: <what is the location of the flat>

        SQM: <square meters>, <number of rooms> 

        Common costs: <common cost> 

        Methods of transportation: <public transportation opportunities> 

        Availability: <when can you move in and whats the downpayment> 

        Recommended for: <what kind of person would like this place and why> 

        Pros: <pros of the apartment>

        Cons: <cons of the apartment>

        Ideal Tenant: <what is the ideal tenant from the perspective of the landlord>

        If you cannot extract information about a specific feature then write N/A as value.
        """
        },
    ]

    @classmethod
    def inference(cls, text):
        response = cls.client.chat.completions.create(
            model= cls.model,
            messages=[*cls.pre_prompts,
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
