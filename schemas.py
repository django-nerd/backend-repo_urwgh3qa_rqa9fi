"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime

# ---------- Domain Schemas ----------

class Category(BaseModel):
    """
    Kategori untuk aplikasi/game
    Nama koleksi: "category"
    """
    name: str = Field(..., description="Nama kategori")
    slug: str = Field(..., description="Slug unik kategori")
    type: Literal["app", "game", "both"] = Field("both", description="Tipe konten di kategori")
    icon: Optional[str] = Field(None, description="Nama icon opsional")

class AppItem(BaseModel):
    """
    Item aplikasi atau game yang dapat diunduh
    Nama koleksi: "appitem"
    """
    title: str = Field(..., description="Judul aplikasi/game")
    slug: str = Field(..., description="Slug unik untuk detail halaman")
    type: Literal["app", "game"] = Field(..., description="Tipe konten")
    short_description: str = Field(..., description="Deskripsi singkat")
    description: str = Field(..., description="Deskripsi lengkap")
    version: str = Field(..., description="Versi saat ini")
    size: str = Field(..., description="Ukuran file, mis. 120 MB")
    category: str = Field(..., description="Slug kategori utama")
    tags: List[str] = Field(default_factory=list, description="Tag terkait")
    features: List[str] = Field(default_factory=list, description="Fitur unggulan")
    screenshots: List[HttpUrl] = Field(default_factory=list, description="URL screenshot")
    download_type: Literal["APK", "XAPK"] = Field("APK", description="Format unduhan")
    download_url: HttpUrl = Field(..., description="URL unduhan")
    updated_at: Optional[datetime] = Field(None, description="Tanggal pembaruan")
    is_premium: bool = Field(False, description="Apakah premium (mod)" )

class BlogPost(BaseModel):
    """
    Artikel blog: tips, tutorial, review
    Nama koleksi: "blogpost"
    """
    title: str = Field(..., description="Judul artikel")
    slug: str = Field(..., description="Slug unik artikel")
    excerpt: str = Field(..., description="Ringkasan singkat")
    content: str = Field(..., description="Konten HTML/Markdown")
    cover_image: Optional[HttpUrl] = Field(None, description="Gambar sampul")
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ContactMessage(BaseModel):
    """
    Pesan dari halaman kontak
    Nama koleksi: "contactmessage"
    """
    name: str = Field(..., description="Nama pengirim")
    email: str = Field(..., description="Email pengirim")
    subject: str = Field(..., description="Subjek")
    message: str = Field(..., description="Isi pesan")

# Contoh lama dipertahankan untuk kompatibilitas (tidak digunakan oleh aplikasi ini)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
