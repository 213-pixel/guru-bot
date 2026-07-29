import os
from groq import Groq
from src.utils.logger import logger
from typing import Optional

class LLMService:
    """Service buat interaksi dengan AI (Groq)"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set! AI features will not work.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
        
        # Model options: llama3-70b-8192, llama3-8b-8192, mixtral-8x7b-32768
        self.model = "llama3-70b-8192"
        logger.info(f"LLM Service initialized with model: {self.model}")
    
    async def chat(self, user_message: str, context: str = "", system_prompt: Optional[str] = None) -> str:
        """
        Kirim pesan ke AI dan dapatkan response
        
        Args:
            user_message: Pesan dari user
            context: Konteks tambahan
            system_prompt: Custom system prompt (opsional)
        
        Returns:
            Response dari AI
        """
        if not self.client:
            return "⚠️ Maaf, fitur AI sedang tidak tersedia. Silakan coba lagi nanti."
        
        try:
            # System prompt default
            default_prompt = """Kamu adalah asisten AI untuk guru di Indonesia. Tugasmu:
1. Membantu menjawab pertanyaan tentang pelajaran (Matematika, IPA, Bahasa, dll)
2. Memberi saran komunikasi efektif dengan orang tua siswa
3. Membantu administrasi kelas ringan
4. Memberi motivasi dan tips mengajar

Aturan:
- Gunakan bahasa Indonesia yang sopan dan profesional
- Jawab dengan jelas dan terstruktur
- Jika tidak tahu, katakan dengan jujur
- Sesuaikan dengan konteks pendidikan di Indonesia
"""
            
            # Gunakan system prompt custom jika ada
            system = system_prompt if system_prompt else default_prompt
            
            # Tambahkan konteks
            full_message = user_message
            if context:
                full_message = f"Konteks: {context}\n\nPertanyaan: {user_message}"
            
            # Panggil Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": full_message}
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
            )
            
            response = completion.choices[0].message.content
            logger.debug(f"AI Response: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "🙏 Maaf, saya mengalami gangguan teknis. Coba tanyakan lagi dalam beberapa saat ya."
    
    async def summarize(self, text: str) -> str:
        """Ringkas teks panjang"""
        prompt = f"Ringkas teks berikut dengan jelas dan padat:\n\n{text}"
        return await self.chat(prompt, system_prompt="Kamu adalah asisten yang ahli merangkum teks.")
    
    async def generate_quiz(self, topic: str, level: str = "SMA") -> str:
        """Generate soal quiz"""
        prompt = f"""Buat 5 soal pilihan ganda tentang {topic} untuk tingkat {level}.
Format:
1. Soal...
   a. Pilihan A
   b. Pilihan B
   c. Pilihan C
   d. Pilihan D
   Jawaban: ...
"""
        return await self.chat(prompt)

# Singleton
llm = LLMService()
