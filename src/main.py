import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Import PostgreSQL utilities
from db_utils import get_pgvector_store, init_database, COLLECTION_NAME

# Tải biến môi trường
load_dotenv()

class HRAssistant:
    def __init__(self, collection_name="hr_documents"):
        # Initialize database to ensure pgvector extension is available
        init_database()
        
        # Setup embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Get PGVector store for retrieval
        self.vectordb = get_pgvector_store(collection_name=collection_name, embedding_function=self.embeddings)
        
        # Setup QA chain
        self.setup_qa_chain()
        
    def setup_qa_chain(self):
        # Tạo prompt template
        template = """Bạn là trợ lý AI của phòng nhân sự. Nhiệm vụ của bạn là trả lời
        các câu hỏi liên quan đến chính sách nhân sự, quy trình tuyển dụng, đào tạo, 
        phúc lợi và các vấn đề nhân sự khác dựa trên tài liệu nội bộ của công ty.

        Hãy chỉ trả lời dựa trên thông tin được cung cấp trong các tài liệu tham khảo dưới đây.
        Nếu không tìm thấy thông tin, hãy thành thật nói rằng bạn không biết hoặc không có
        thông tin trong tài liệu. Không tự nghĩ ra thông tin.

        Tài liệu tham khảo:
        {context}

        Câu hỏi: {question}
        """
        QA_PROMPT = PromptTemplate(
            template=template, 
            input_variables=["context", "question"]
        )
        
        # Sử dụng Gemini 1.0 Pro (miễn phí có giới hạn)
        # llm = ChatGoogleGenerativeAI(
        #     model="gemini-1.0-pro",  # Mô hình miễn phí
        #     temperature=0.1,
        #     max_output_tokens=512,
        #     google_api_key=os.getenv("GOOGLE_API_KEY")
        # )

        # # HOẶC

        # # Sử dụng Gemini 1.5 Flash (miễn phí có giới hạn, hiệu suất tốt hơn)
        # llm = ChatGoogleGenerativeAI(
        #     model="gemini-1.5-flash",  # Mô hình miễn phí, hiệu suất tốt hơn
        #     temperature=0.1,
        #     max_output_tokens=512,
        #     google_api_key=os.getenv("GOOGLE_API_KEY")
        # )

        # Gemini 1.5 Pro - Không Miễn Phí
        # Không, gemini-1.5-pro không miễn phí. Đây là mô hình cao cấp của Google với chi phí như sau:
        # Đầu vào: $7.00 cho 1 triệu token
        # Đầu ra: $21.00 cho 1 triệu token
        # Tuy nhiên, Google thường cung cấp hạn ngạch miễn phí ban đầu khi bạn đăng ký mới (thường là $300 tín dụng Google Cloud trong 90 ngày), có thể dùng để thử nghiệm Gemini.

        # Use Google Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",  # Using Gemini 1.5 Pro model
            temperature=0.1,  # Lower temperature for more focused responses
            max_output_tokens=512,   # Maximum tokens to generate
            google_api_key=os.getenv("GOOGLE_API_KEY")  # Using the provided API key
        )
        
        # Use standard RetrievalQA chain with local LLM
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # Simple document concatenation
            retriever=self.vectordb.as_retriever(search_kwargs={"k": 3}),  # Reduced context
            chain_type_kwargs={"prompt": QA_PROMPT},
            return_source_documents=False,  # Don't include source docs in output
            verbose=False
        )
   
    
    def ask(self, question):
        """Trả lời câu hỏi của người dùng"""
        try:
            # Using invoke method with query key as expected by RetrievalQA
            response = self.qa_chain.invoke({"query": question})
            
            # Handle different return formats
            if isinstance(response, dict) and "result" in response:
                return response["result"]
            elif isinstance(response, str):
                return response
            else:
                return str(response)  # Fallback to string representation
        except Exception as e:
            return f"Gặp lỗi khi xử lý câu hỏi: {str(e)}"

# Singleton instance
hr_assistant = HRAssistant()

def get_assistant():
    return hr_assistant
