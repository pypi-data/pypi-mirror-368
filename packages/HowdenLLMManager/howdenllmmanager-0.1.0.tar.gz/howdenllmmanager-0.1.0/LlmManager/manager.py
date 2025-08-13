from dotenv import load_dotenv
import time
import os

def llm_factory(
        full_model_name : str,
):

    load_dotenv()  # Loads variables from .env into environment

    if full_model_name.startswith("openai:"):
        from langchain_community.chat_models import ChatOpenAI
        from langchain.chains.question_answering import load_qa_chain
        from langchain.schema import Document

        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY is not set in environment variables.")

        openai_model_name = full_model_name.split("openai:")[1]
        llm = ChatOpenAI(model=openai_model_name, temperature=0)

        # Your input text as a string
        input_text = "Hugging Face is a company based in New York that specializes in natural language processing."

        # Wrap input text in a Document (LangChain expects docs)
        docs = [Document(page_content=input_text)]

        # Load a QA chain with "stuff" method (no vectorstore, no retrieval)
        qa_chain = load_qa_chain(llm, chain_type="stuff")

        # Your question
        question = "Where is Hugging Face based?"

        start = time.time()
        result = qa_chain.run(input_documents=docs, question=question)
        end = time.time()

        print(f"Question answering time: {end - start:.2f} seconds")
        print("Answer:", result)

    elif full_model_name.startswith("huggingface:"):
        from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
        from huggingface_hub import snapshot_download

        model_name = full_model_name.split("huggingface:")[1]
        cache_dir = "./hf_cache"

        start = time.time()
        local_path = snapshot_download(model_name, cache_dir=cache_dir, resume_download=False)
        end = time.time()
        print(f"Model download time: {end - start:.2f} seconds")

        if os.path.exists(local_path):
            print("Model is already downloaded.")
        else:
            print("Model is not downloaded.")

        start = time.time()
        model = AutoModelForQuestionAnswering.from_pretrained(model_name, cache_dir=cache_dir)
        end = time.time()
        print(f"Model loading time: {end - start:.2f} seconds")

        start = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        end = time.time()
        print(f"Tokenizer loading time: {end - start:.2f} seconds")

        start = time.time()
        qa_pipeline = pipeline(
            "question-answering",
            model=model,
            tokenizer=tokenizer
        )
        end = time.time()
        print(f"Pipeline setup time: {end - start:.2f} seconds")

        context = "Hugging Face is a company based in New York that specializes in natural language processing."
        question = "Where is Hugging Face based?"

        start = time.time()
        result = qa_pipeline(question=question, context=context)
        end = time.time()
        print(f"Question answering time: {end - start:.2f} seconds")

        print("Answer:", result['answer'])
        print("Confidence score:", result['score'])
        print(context[result['start']:result['end']])  # prints "New York"    else:
    else:
        raise ValueError(
            f"Unsupported model_name '{full_model_name}'. Use 'openai:' or 'huggingface:' prefix."
        )
