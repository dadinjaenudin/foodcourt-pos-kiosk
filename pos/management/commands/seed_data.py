from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from pos.models import Tenant, Category, Product, Order, OrderItem
import requests
import os
import random


# Image URLs from generated images
TENANT_LOGOS = {
    'ramen-sanpachi': 'https://www.genspark.ai/api/files/s/cXmU4rQs?cache_control=3600',
    'korean-house': 'https://www.genspark.ai/api/files/s/kwCOaWNZ?cache_control=3600',
    'pizza-bella': 'https://www.genspark.ai/api/files/s/wQrbNT5v?cache_control=3600',
    'rumah-padang': 'https://www.genspark.ai/api/files/s/F04NWZMs?cache_control=3600',
    'burger-bros': 'https://www.genspark.ai/api/files/s/gjeTZ5Hf?cache_control=3600',
    'thai-orchid': 'https://www.genspark.ai/api/files/s/WEAD4sBd?cache_control=3600',
    'dim-sum-palace': 'https://www.genspark.ai/api/files/s/WfxPMI4N?cache_control=3600',
    'boba-paradise': 'https://www.genspark.ai/api/files/s/7UQxzZpr?cache_control=3600',
    'taco-fiesta': 'https://www.genspark.ai/api/files/s/MhZDgH6K?cache_control=3600',
    'sweet-moments': 'https://www.genspark.ai/api/files/s/jjmazkcB?cache_control=3600',
}

PRODUCT_IMAGES = {
    'ramen': 'https://www.genspark.ai/api/files/s/NZjXv11S?cache_control=3600',
    'korean': 'https://www.genspark.ai/api/files/s/DNd3UWPN?cache_control=3600',
    'pizza': 'https://www.genspark.ai/api/files/s/FVp1UjSk?cache_control=3600',
    'padang': 'https://www.genspark.ai/api/files/s/xmkCePzk?cache_control=3600',
    'burger': 'https://www.genspark.ai/api/files/s/waxviT3X?cache_control=3600',
    'thai': 'https://www.genspark.ai/api/files/s/MVsTKzFT?cache_control=3600',
    'dimsum': 'https://www.genspark.ai/api/files/s/sBGl0pq8?cache_control=3600',
    'boba': 'https://www.genspark.ai/api/files/s/3BYvX0Cn?cache_control=3600',
    'taco': 'https://www.genspark.ai/api/files/s/lSMOMCJM?cache_control=3600',
    'dessert': 'https://www.genspark.ai/api/files/s/Tm5j0Mcr?cache_control=3600',
}


TENANTS_DATA = [
    {
        'name': 'Ramen Sanpachi',
        'slug': 'ramen-sanpachi',
        'description': 'Sajian ramen autentik Jepang dengan kaldu tonkotsu 18 jam, topping premium pilihan, dan chashu pork lembut. Dibuat dengan cinta oleh koki berpengalaman dari Osaka.',
        'cuisine_type': 'japanese',
        'stall_number': 'A01',
        'banner_color': '#DC2626',
        'secondary_color': '#FCA5A5',
        'icon_emoji': '🍜',
        'rating': 4.8,
        'total_orders': 2847,
        'categories': ['Ramen', 'Tsukemen', 'Donburi', 'Minuman'],
        'products': [
            {'name': 'Tonkotsu Ramen', 'desc': 'Kaldu babi kental 18 jam, chashu pork, telur ajitsuke, nori, spring onion, bamboo shoot', 'price': 65000, 'calories': 650, 'best': True, 'featured': True, 'time': 12},
            {'name': 'Shoyu Ramen', 'desc': 'Kaldu ayam ringan dengan kecap jepang, chicken chashu, narutomaki, menma', 'price': 58000, 'calories': 520, 'time': 10},
            {'name': 'Miso Ramen', 'desc': 'Kaldu miso kaya umami, corn, butter, topping nori dan bawang merah goreng', 'price': 62000, 'calories': 580, 'time': 12, 'spicy': True},
            {'name': 'Spicy Tantanmen', 'desc': 'Ramen pedas ala Sichuan dengan daging cincang, biji wijen, dan minyak cabai premium', 'price': 68000, 'calories': 700, 'spicy': True, 'time': 12},
            {'name': 'Gyoza (6 pcs)', 'desc': 'Pangsit panggang renyah berisi daging babi dan sayuran, disajikan dengan saus ponzu', 'price': 35000, 'calories': 280, 'time': 8, 'best': True},
            {'name': 'Karaage Chicken', 'desc': 'Ayam goreng Jepang marinade shoyu dan jahe, renyah di luar, juicy di dalam', 'price': 48000, 'calories': 420, 'time': 10},
            {'name': 'Chashu Don', 'desc': 'Rice bowl dengan chashu pork berlapis, telur onsen, dan saus tare special', 'price': 55000, 'calories': 580, 'time': 10},
            {'name': 'Tsukemen', 'desc': 'Mie tebal disajikan terpisah dengan kuah celup pekat kaya rasa umami', 'price': 70000, 'calories': 620, 'featured': True, 'time': 15},
            {'name': 'Matcha Latte', 'desc': 'Minuman matcha creamy dengan susu full cream, rasa autentik Jepang', 'price': 32000, 'calories': 180, 'time': 5, 'veg': True},
            {'name': 'Ramune Soda', 'desc': 'Soda khas Jepang dengan rasa stroberi/melon/original dalam botol unik', 'price': 25000, 'calories': 120, 'time': 2, 'veg': True},
        ]
    },
    {
        'name': 'Korean House',
        'slug': 'korean-house',
        'description': 'Pengalaman BBQ Korea terbaik dengan daging segar grade A, banchan pilihan, dan saus gochujang homemade. Hadirkan suasana pojangmacha Seoul di tengah kota.',
        'cuisine_type': 'korean',
        'stall_number': 'A02',
        'banner_color': '#B91C1C',
        'secondary_color': '#FEF08A',
        'icon_emoji': '🥩',
        'rating': 4.7,
        'total_orders': 1932,
        'categories': ['BBQ', 'Rice & Noodle', 'Soup', 'Dessert'],
        'products': [
            {'name': 'Galbi BBQ', 'desc': 'Iga sapi marinasi gaya Korea, dipanggang sempurna, disajikan dengan ssam dan banchan lengkap', 'price': 95000, 'calories': 580, 'best': True, 'featured': True, 'time': 20},
            {'name': 'Samgyeopsal', 'desc': 'Perut babi segar dipanggang, disajikan dengan kimchi, bawang putih, dan ssamjang', 'price': 85000, 'calories': 650, 'time': 18},
            {'name': 'Bibimbap', 'desc': 'Nasi campur Korea dengan sayuran segar, daging sapi, telur, dan gochujang', 'price': 55000, 'calories': 480, 'best': True, 'time': 10, 'veg': True},
            {'name': 'Tteokbokki', 'desc': 'Kue beras pedas dengan saus gochujang, fish cake, dan telur rebus', 'price': 45000, 'calories': 380, 'spicy': True, 'time': 12},
            {'name': 'Kimchi Jjigae', 'desc': 'Sup kimchi hangat dengan tofu, daging babi, dan sayuran, cocok untuk cuaca dingin', 'price': 52000, 'calories': 320, 'spicy': True, 'time': 15},
            {'name': 'Bulgogi', 'desc': 'Daging sapi marinasi manis-gurih, dipanggang tipis, disajikan dengan nasi dan banchan', 'price': 72000, 'calories': 420, 'featured': True, 'time': 15},
            {'name': 'Japchae', 'desc': 'Mie glass noodle tumis dengan sayuran segar dan daging sapi, rasa manis gurih', 'price': 48000, 'calories': 350, 'time': 12, 'veg': True},
            {'name': 'Korean Fried Chicken', 'desc': 'Ayam goreng crispy Korea dengan saus honey butter atau saus pedas', 'price': 68000, 'calories': 520, 'best': True, 'time': 15},
            {'name': 'Sundubu Jjigae', 'desc': 'Sup tofu lembut yang pedas dengan seafood segar dan sayuran', 'price': 58000, 'calories': 280, 'spicy': True, 'time': 15},
            {'name': 'Bingsu Strawberry', 'desc': 'Es serut Korea dengan topping stroberi segar, red bean, mochi, dan susu kondensed', 'price': 42000, 'calories': 320, 'time': 8, 'veg': True},
        ]
    },
    {
        'name': 'Pizza Bella',
        'slug': 'pizza-bella',
        'description': 'Pizza Italia autentik dengan adonan hand-tossed 72 jam, saus tomat San Marzano, dan mozzarella premium. Dipanggang dalam oven batu asli untuk cita rasa sempurna.',
        'cuisine_type': 'italian',
        'stall_number': 'B01',
        'banner_color': '#16A34A',
        'secondary_color': '#FCA5A5',
        'icon_emoji': '🍕',
        'rating': 4.6,
        'total_orders': 1567,
        'categories': ['Pizza', 'Pasta', 'Salad & Soup', 'Minuman'],
        'products': [
            {'name': 'Margherita Classica', 'desc': 'Saus tomat San Marzano, mozzarella fior di latte, basil segar, drizzle olive oil premium', 'price': 72000, 'calories': 680, 'veg': True, 'best': True, 'featured': True, 'time': 18},
            {'name': 'Prosciutto e Funghi', 'desc': 'Pizza dengan prosciutto crudo, mushroom porcini, mozzarella, dan rocket salad', 'price': 88000, 'calories': 720, 'time': 18},
            {'name': 'Diavola', 'desc': 'Pizza pedas dengan salami piccante, chili, mozzarella, dan tomat cherry', 'price': 82000, 'calories': 710, 'spicy': True, 'best': True, 'time': 18},
            {'name': 'Quattro Formaggi', 'desc': 'Empat keju pilihan: mozzarella, gorgonzola, parmigiano reggiano, dan fontina', 'price': 92000, 'calories': 850, 'veg': True, 'featured': True, 'time': 18},
            {'name': 'Spaghetti Carbonara', 'desc': 'Pasta telur dengan guanciale, pecorino romano, pepe nero, autentik gaya Roma', 'price': 68000, 'calories': 620, 'time': 15},
            {'name': 'Penne Arrabbiata', 'desc': 'Pasta pedas dengan saus tomat, bawang putih, chili flakes, dan parmigiano', 'price': 62000, 'calories': 540, 'spicy': True, 'veg': True, 'time': 12},
            {'name': 'Lasagna Bolognese', 'desc': 'Lasagna berlapis dengan ragù sapi, béchamel, dan keju parmigiano berlimpah', 'price': 78000, 'calories': 750, 'best': True, 'time': 20},
            {'name': 'Caesar Salad', 'desc': 'Romaine segar, crouton homemade, anchovy, parmigiano, saus caesar klasik', 'price': 52000, 'calories': 280, 'time': 8},
            {'name': 'Tiramisu', 'desc': 'Dessert Italia klasik dengan mascarpone, savoiardi, espresso, cocoa powder', 'price': 45000, 'calories': 380, 'veg': True, 'time': 5},
            {'name': 'Italian Soda', 'desc': 'Soda Italia dengan sirup jeruk/raspberry/lemon, segar dan menyegarkan', 'price': 28000, 'calories': 150, 'veg': True, 'time': 3},
        ]
    },
    {
        'name': 'Rumah Padang',
        'slug': 'rumah-padang',
        'description': 'Masakan Minangkabau autentik dengan bumbu rempah pilihan dan dimasak sesuai resep turun temurun. Rendang terbaik dengan daging premium dan santan kelapa segar.',
        'cuisine_type': 'indonesian',
        'stall_number': 'B02',
        'banner_color': '#CA8A04',
        'secondary_color': '#86EFAC',
        'icon_emoji': '🍛',
        'rating': 4.9,
        'total_orders': 3421,
        'categories': ['Nasi', 'Lauk Pauk', 'Gulai & Sup', 'Minuman'],
        'products': [
            {'name': 'Nasi Rendang', 'desc': 'Nasi putih pulen dengan rendang sapi matang sempurna, 8 jam dimasak, rempah kaya cita rasa', 'price': 55000, 'calories': 680, 'best': True, 'featured': True, 'time': 10},
            {'name': 'Nasi Padang Komplit', 'desc': 'Nasi putih dengan 5 lauk pilihan: rendang, ayam pop, gulai tahu, perkedel, sambal hijau', 'price': 68000, 'calories': 850, 'best': True, 'time': 8, 'spicy': True},
            {'name': 'Ayam Pop', 'desc': 'Ayam kampung rebus bumbu kuning, digoreng sebentar, tekstur lembut empuk', 'price': 38000, 'calories': 320, 'time': 10},
            {'name': 'Gulai Kambing', 'desc': 'Gulai kambing santan kental dengan rempah pilihan, empuk dan kaya cita rasa', 'price': 62000, 'calories': 450, 'featured': True, 'time': 12},
            {'name': 'Sate Padang', 'desc': 'Sate daging sapi dengan kuah sate Padang khas berwarna kuning, disajikan dengan lontong', 'price': 52000, 'calories': 380, 'best': True, 'time': 12, 'spicy': True},
            {'name': 'Gulai Ikan Kakap', 'desc': 'Ikan kakap merah dalam kuah gulai santan kuning dengan terong dan tomat hijau', 'price': 58000, 'calories': 380, 'time': 10, 'spicy': True},
            {'name': 'Perkedel Jagung', 'desc': 'Bakwan jagung crispy dengan bumbu daun bawang dan sedikit udang cincang', 'price': 22000, 'calories': 180, 'time': 8, 'veg': True},
            {'name': 'Sayur Singkong', 'desc': 'Daun singkong muda dimasak santan dengan teri Medan dan cabai merah', 'price': 18000, 'calories': 120, 'time': 5, 'veg': True},
            {'name': 'Es Teh Tarik', 'desc': 'Teh tarik khas Minang dengan sedikit kental manis, segar dan creamy', 'price': 15000, 'calories': 120, 'time': 3, 'veg': True},
            {'name': 'Es Jeruk Peras', 'desc': 'Jeruk segar diperas langsung, manis segar, cocok dengan makanan bersantan', 'price': 18000, 'calories': 80, 'time': 3, 'veg': True},
        ]
    },
    {
        'name': 'Burger Bros',
        'slug': 'burger-bros',
        'description': 'Smash burger premium dengan daging sapi wagyu lokal, roti brioche artisan panggang, dan saus secret recipe. Kombinasi juicy, crispy, dan penuh cita rasa!',
        'cuisine_type': 'american',
        'stall_number': 'C01',
        'banner_color': '#DC2626',
        'secondary_color': '#FDE047',
        'icon_emoji': '🍔',
        'rating': 4.7,
        'total_orders': 2156,
        'categories': ['Burger', 'Sides', 'Hotdog', 'Minuman'],
        'products': [
            {'name': 'The Classic Smash', 'desc': 'Double beef patty smash 150g, american cheese, lettuce, tomato, pickles, secret sauce, brioche bun', 'price': 78000, 'calories': 780, 'best': True, 'featured': True, 'time': 12},
            {'name': 'BBQ Bacon Monster', 'desc': 'Triple patty, bacon crispy, BBQ sauce smoky, caramelized onion, cheddar cheese melt', 'price': 95000, 'calories': 980, 'time': 15, 'best': True},
            {'name': 'Mushroom Swiss', 'desc': 'Beef patty dengan sautéed mushroom, swiss cheese melt, truffle mayo premium', 'price': 85000, 'calories': 750, 'featured': True, 'time': 12},
            {'name': 'Spicy Jalapeño', 'desc': 'Beef patty, jalapeño segar, pepper jack cheese, sriracha aioli, crispy onion ring', 'price': 82000, 'calories': 820, 'spicy': True, 'time': 12},
            {'name': 'Crispy Chicken Burger', 'desc': 'Ayam crispy buttermilk fried, coleslaw segar, pickle, honey mustard sauce', 'price': 72000, 'calories': 680, 'time': 12},
            {'name': 'Smash Fries', 'desc': 'Kentang goreng crispy dengan seasoning khusus dan dipping sauce pilihan', 'price': 32000, 'calories': 380, 'veg': True, 'best': True, 'time': 8},
            {'name': 'Onion Rings', 'desc': 'Bawang bombay tepung renyah dengan ranch dipping sauce, crispy dan gurih', 'price': 35000, 'calories': 320, 'veg': True, 'time': 8},
            {'name': 'Chili Dog', 'desc': 'Hotdog beef premium dengan chili meat sauce, mustard, dan pickled jalapeño', 'price': 58000, 'calories': 520, 'spicy': True, 'time': 10},
            {'name': 'Milkshake Vanilla', 'desc': 'Milkshake creamy vanilla dengan whipped cream dan cherry, thick dan lezat', 'price': 42000, 'calories': 480, 'veg': True, 'time': 5},
            {'name': 'Root Beer Float', 'desc': 'Root beer dingin dengan scoop es krim vanilla, klasik American style', 'price': 38000, 'calories': 350, 'veg': True, 'time': 3},
        ]
    },
    {
        'name': 'Thai Orchid',
        'slug': 'thai-orchid',
        'description': 'Street food Thailand autentik dengan bumbu rempah impor langsung dari Bangkok. Rasakan sensasi pedas, asam, manis, dan gurih khas masakan Thai yang sesungguhnya.',
        'cuisine_type': 'thai',
        'stall_number': 'C02',
        'banner_color': '#7C3AED',
        'secondary_color': '#FDE047',
        'icon_emoji': '🌶️',
        'rating': 4.6,
        'total_orders': 1298,
        'categories': ['Rice & Noodle', 'Soup', 'Salad', 'Dessert'],
        'products': [
            {'name': 'Pad Thai Goong', 'desc': 'Mie beras tumis dengan udang segar, tahu, tauge, kacang tanah, dan telur, saus tamarind', 'price': 62000, 'calories': 520, 'best': True, 'featured': True, 'time': 12},
            {'name': 'Green Curry Chicken', 'desc': 'Kari hijau ayam dengan santan kelapa, terong Thai, basil segar, dan daun jeruk', 'price': 58000, 'calories': 420, 'spicy': True, 'time': 15, 'featured': True},
            {'name': 'Tom Yum Goong', 'desc': 'Sup udang pedas asam dengan galangal, serai, jamur, daun jeruk kaffir, dan cabai', 'price': 65000, 'calories': 280, 'spicy': True, 'best': True, 'time': 15},
            {'name': 'Massaman Beef', 'desc': 'Kari massaman daging sapi dengan kentang, bawang, kacang mete, dan rempah halus', 'price': 72000, 'calories': 480, 'time': 20},
            {'name': 'Khao Man Gai', 'desc': 'Nasi ayam Thailand dengan ayam rebus, kuah kaldu jernih, dan saus jahe pedas', 'price': 52000, 'calories': 450, 'time': 12},
            {'name': 'Som Tum', 'desc': 'Salad pepaya muda pedas dengan tomat cherry, kacang panjang, udang kering, lime', 'price': 45000, 'calories': 180, 'spicy': True, 'veg': True, 'time': 8},
            {'name': 'Mango Sticky Rice', 'desc': 'Ketan manis dengan mangga muda/matang segar, santan pandan, biji wijen panggang', 'price': 42000, 'calories': 380, 'veg': True, 'time': 5},
            {'name': 'Pad Kra Pao', 'desc': 'Tumisan daging sapi/ayam dengan basil Thailand, saus oister, telur mata sapi', 'price': 55000, 'calories': 380, 'spicy': True, 'time': 12},
            {'name': 'Thai Iced Tea', 'desc': 'Teh Thailand orange khas dengan susu evaporasi, manis dan segar', 'price': 25000, 'calories': 180, 'veg': True, 'time': 3},
            {'name': 'Lemongrass Refresher', 'desc': 'Minuman serai segar dengan lemon, gula aren, dan daun mint, unik dan menyegarkan', 'price': 28000, 'calories': 90, 'veg': True, 'time': 3},
        ]
    },
    {
        'name': 'Dim Sum Palace',
        'slug': 'dim-sum-palace',
        'description': 'Dim sum tradisional Kanton dengan bahan premium segar. Setiap dumpling dibuat tangan oleh sifu berpengalaman 30 tahun. Nikmati yum cha experience terbaik.',
        'cuisine_type': 'chinese',
        'stall_number': 'D01',
        'banner_color': '#DC2626',
        'secondary_color': '#FDE047',
        'icon_emoji': '🥟',
        'rating': 4.8,
        'total_orders': 2089,
        'categories': ['Dim Sum', 'Congee & Noodle', 'BBQ', 'Dessert'],
        'products': [
            {'name': 'Har Gow (4pcs)', 'desc': 'Dumpling udang crystal skin tipis transparan, udang segar crispy, classic dim sum', 'price': 38000, 'calories': 180, 'best': True, 'featured': True, 'time': 10},
            {'name': 'Siu Mai (4pcs)', 'desc': 'Dumpling terbuka berisi daging babi dan udang, topped dengan roe dan wortel', 'price': 35000, 'calories': 200, 'best': True, 'time': 10},
            {'name': 'Char Siu Bao (3pcs)', 'desc': 'Bakpao daging BBQ empuk, isian char siu manis-gurih, baked atau steamed', 'price': 32000, 'calories': 280, 'time': 8, 'featured': True},
            {'name': 'Lo Mai Gai', 'desc': 'Ketan ayam dibungkus daun lotus, dikukus, kaya rasa dengan jamur dan sosis', 'price': 42000, 'calories': 380, 'time': 12},
            {'name': 'Chee Cheong Fun', 'desc': 'Kulit beras lembut isi udang/BBQ pork, disajikan dengan saus kecap sweet manis', 'price': 35000, 'calories': 220, 'time': 8},
            {'name': 'Congee Century Egg', 'desc': 'Bubur beras halus dengan century egg, jahe julienne, spring onion, dan you tiao', 'price': 45000, 'calories': 280, 'time': 12},
            {'name': 'Roasted Duck', 'desc': 'Bebek panggang dengan kulit renyah berkilau, disajikan dengan hoisin sauce', 'price': 85000, 'calories': 520, 'time': 15, 'best': True},
            {'name': 'Wonton Noodle', 'desc': 'Mie egg noodle tipis dengan wonton udang, dalam kuah kaldu jernih atau kering', 'price': 52000, 'calories': 380, 'time': 10},
            {'name': 'Egg Tart', 'desc': 'Tart telur custard creamy dalam kulit pastry flaky tipis, hangat dan lembut', 'price': 25000, 'calories': 220, 'veg': True, 'time': 5},
            {'name': 'Chrysanthemum Tea', 'desc': 'Teh bunga krisan hangat yang menyegarkan, herbal dan ringan', 'price': 18000, 'calories': 20, 'veg': True, 'time': 3},
        ]
    },
    {
        'name': 'Boba Paradise',
        'slug': 'boba-paradise',
        'description': 'Bubble tea dan minuman premium dengan bahan berkualitas tinggi. Dari teh segar, susu segar, hingga topping handmade. Tersedia 50+ pilihan rasa yang bisa dikustomisasi.',
        'cuisine_type': 'beverage',
        'stall_number': 'D02',
        'banner_color': '#7C3AED',
        'secondary_color': '#F9A8D4',
        'icon_emoji': '🧋',
        'rating': 4.5,
        'total_orders': 4521,
        'categories': ['Bubble Tea', 'Milk Tea', 'Fresh Juice', 'Smoothie'],
        'products': [
            {'name': 'Brown Sugar Boba', 'desc': 'Milk tea dengan gula aren karamel, pearl boba tebal kenyal, susu fresh, es', 'price': 35000, 'calories': 380, 'best': True, 'featured': True, 'veg': True, 'time': 5},
            {'name': 'Matcha Boba Latte', 'desc': 'Matcha Uji Kyoto premium dengan susu oat/regular, boba original, creamy dan earthy', 'price': 38000, 'calories': 320, 'veg': True, 'time': 5, 'best': True},
            {'name': 'Taro Milk Tea', 'desc': 'Teh talas ungu creamy dengan boba, sedikit manis dan aroma talas yang khas', 'price': 35000, 'calories': 350, 'veg': True, 'time': 5},
            {'name': 'Mango Passion', 'desc': 'Mangga segar blend dengan passion fruit tea, popping boba, segar dan tropis', 'price': 40000, 'calories': 280, 'veg': True, 'featured': True, 'time': 5},
            {'name': 'Strawberry Smoothie', 'desc': 'Stroberi segar blend dengan yogurt, madu, dan susu, tanpa tambahan gula artifisial', 'price': 38000, 'calories': 220, 'veg': True, 'time': 5},
            {'name': 'Avocado Coffee', 'desc': 'Alpukat segar dengan espresso shot, susu segar, dan gula aren, trending combo', 'price': 42000, 'calories': 380, 'veg': True, 'best': True, 'time': 5},
            {'name': 'Fresh Orange Juice', 'desc': 'Jeruk sunkist diperas langsung, 100% segar tanpa tambahan apapun', 'price': 28000, 'calories': 120, 'veg': True, 'time': 5},
            {'name': 'Lychee Sparkling', 'desc': 'Air leci dengan soda, jelly leci, dan irisan lemon, segar dan ringan', 'price': 32000, 'calories': 150, 'veg': True, 'time': 3},
            {'name': 'Tiger Milk Tea', 'desc': 'Milk tea dengan tiger stripes gula aren di dinding gelas, boba chewy dan creamy', 'price': 38000, 'calories': 360, 'veg': True, 'time': 5},
            {'name': 'Coconut Fresh', 'desc': 'Air kelapa muda segar langsung dari kelapa, ditambah sedikit grass jelly', 'price': 30000, 'calories': 90, 'veg': True, 'time': 3},
        ]
    },
    {
        'name': 'Taco Fiesta',
        'slug': 'taco-fiesta',
        'description': 'Masakan Meksiko autentik dengan tortilla handmade segar, daging marinated sempurna, dan salsa segar buatan setiap hari. Fiesta rasa di setiap gigitan!',
        'cuisine_type': 'mexican',
        'stall_number': 'E01',
        'banner_color': '#EA580C',
        'secondary_color': '#FDE047',
        'icon_emoji': '🌮',
        'rating': 4.4,
        'total_orders': 987,
        'categories': ['Taco', 'Burrito', 'Nachos', 'Minuman'],
        'products': [
            {'name': 'Taco al Pastor', 'desc': 'Tortilla corn dengan daging babi marinated achiote, nanas, cilantro, dan salsa verde', 'price': 48000, 'calories': 380, 'best': True, 'featured': True, 'time': 8, 'spicy': True},
            {'name': 'Carnitas Burrito', 'desc': 'Burrito besar dengan slow-cooked pork, rice, beans, guacamole, sour cream, cheese', 'price': 72000, 'calories': 780, 'best': True, 'time': 10},
            {'name': 'Chicken Quesadilla', 'desc': 'Tortilla crispy isi ayam berbumbu, keju mozzarella melt, peppers, dan pico de gallo', 'price': 58000, 'calories': 520, 'time': 10, 'featured': True},
            {'name': 'Nachos Supremo', 'desc': 'Tortilla chips crispy dengan queso fundido, guacamole segar, jalapeño, sour cream', 'price': 65000, 'calories': 680, 'veg': True, 'spicy': True, 'time': 8},
            {'name': 'Fish Taco Baja', 'desc': 'Ikan putih crispy, cabbage slaw, salsa mango, crema, dan chipotle mayo', 'price': 55000, 'calories': 420, 'time': 10},
            {'name': 'Elote', 'desc': 'Jagung panggang Meksiko dengan mayo, cotija cheese, chili powder, dan lime', 'price': 35000, 'calories': 320, 'veg': True, 'time': 8},
            {'name': 'Enchiladas Rojas', 'desc': 'Tortilla isi chicken dengan saus merah chili, keju, onion, dan sour cream', 'price': 62000, 'calories': 580, 'spicy': True, 'time': 15},
            {'name': 'Churros con Chocolate', 'desc': 'Churros goreng renyah tabur kayu manis gula dengan saus coklat hangat untuk dicelup', 'price': 38000, 'calories': 420, 'veg': True, 'time': 8, 'best': True},
            {'name': 'Horchata', 'desc': 'Minuman beras khas Meksiko dengan kayu manis dan vanila, manis segar dan creamy', 'price': 25000, 'calories': 180, 'veg': True, 'time': 3},
            {'name': 'Margarita Mocktail', 'desc': 'Virgin margarita dengan lime segar, garam, dan simple syrup, segar dan asam', 'price': 32000, 'calories': 120, 'veg': True, 'time': 3},
        ]
    },
    {
        'name': 'Sweet Moments',
        'slug': 'sweet-moments',
        'description': 'Dessert premium dengan kreasi unik dan bahan-bahan berkualitas tinggi. Dari waffle artisan hingga gelato Italia, setiap kreasi adalah momen manis yang tak terlupakan.',
        'cuisine_type': 'dessert',
        'stall_number': 'E02',
        'banner_color': '#DB2777',
        'secondary_color': '#E879F9',
        'icon_emoji': '🍨',
        'rating': 4.9,
        'total_orders': 3102,
        'categories': ['Waffle', 'Ice Cream', 'Cake', 'Drinks'],
        'products': [
            {'name': 'Waffle Strawberry Dream', 'desc': 'Waffle Belgium crispy dengan es krim stroberi, fresh strawberry, whipped cream, chocolate drizzle', 'price': 68000, 'calories': 680, 'veg': True, 'best': True, 'featured': True, 'time': 12},
            {'name': 'Chocolate Lava Cake', 'desc': 'Kue coklat fondant lava mengalir dengan vanilla ice cream dan raspberry coulis', 'price': 58000, 'calories': 550, 'veg': True, 'best': True, 'time': 15},
            {'name': 'Matcha Parfait', 'desc': 'Parfait matcha dengan granola, yogurt, red bean, mochi, dan matcha ice cream', 'price': 62000, 'calories': 480, 'veg': True, 'featured': True, 'time': 8},
            {'name': 'Gelato Trio', 'desc': 'Tiga pilihan gelato: pistachio, salted caramel, dan dark chocolate premium Italia', 'price': 55000, 'calories': 380, 'veg': True, 'time': 5},
            {'name': 'Crepe Nutella Berry', 'desc': 'Crepe tipis lembut dengan nutella, mixed berry segar, powdered sugar, dan mint', 'price': 52000, 'calories': 520, 'veg': True, 'time': 10},
            {'name': 'Oreo Cheesecake', 'desc': 'Cheesecake no-bake dengan base oreo, cream cheese lembut, dan topping oreo crumble', 'price': 58000, 'calories': 580, 'veg': True, 'time': 5, 'best': True},
            {'name': 'Crème Brûlée', 'desc': 'Custard vanilla Prancis dengan topping karamel renyah dibakar saat order, elegant', 'price': 65000, 'calories': 420, 'veg': True, 'time': 8},
            {'name': 'Banana Foster Waffle', 'desc': 'Waffle dengan pisang caramelized, rum sauce, vanilla ice cream, dan pecan', 'price': 72000, 'calories': 720, 'veg': True, 'time': 12},
            {'name': 'Fruity Bubble Waffle', 'desc': 'Egg waffle Hong Kong style dengan es krim, buah segar, dan saus pilihan', 'price': 65000, 'calories': 580, 'veg': True, 'featured': True, 'time': 12},
            {'name': 'Hot Chocolate Premium', 'desc': 'Coklat panas Belgium 70% dark dengan susu full cream, marshmallow, dan cinnamon', 'price': 38000, 'calories': 280, 'veg': True, 'time': 5},
        ]
    },
]


class Command(BaseCommand):
    help = 'Seed database with food court data and download product images'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting food court data seeding...'))
        
        # Clear existing data
        self.stdout.write('🗑️  Clearing existing data...')
        OrderItem.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Tenant.objects.all().delete()
        
        # Download images
        self.stdout.write('📸 Downloading tenant logos...')
        tenant_logo_files = {}
        for slug, url in TENANT_LOGOS.items():
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    tenant_logo_files[slug] = ContentFile(response.content, name=f'{slug}_logo.jpg')
                    self.stdout.write(f'  ✅ Downloaded logo for {slug}')
                else:
                    self.stdout.write(f'  ⚠️ Failed to download logo for {slug}')
            except Exception as e:
                self.stdout.write(f'  ❌ Error downloading logo for {slug}: {e}')
        
        self.stdout.write('📸 Downloading product images...')
        product_image_files = {}
        for key, url in PRODUCT_IMAGES.items():
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    product_image_files[key] = response.content
                    self.stdout.write(f'  ✅ Downloaded product image: {key}')
                else:
                    self.stdout.write(f'  ⚠️ Failed to download product image: {key}')
            except Exception as e:
                self.stdout.write(f'  ❌ Error downloading product image {key}: {e}')
        
        # Category image mapping
        cuisine_to_img = {
            'japanese': 'ramen',
            'korean': 'korean',
            'italian': 'pizza',
            'indonesian': 'padang',
            'american': 'burger',
            'thai': 'thai',
            'chinese': 'dimsum',
            'beverage': 'boba',
            'mexican': 'taco',
            'dessert': 'dessert',
        }
        
        # Create tenants and products
        for tenant_data in TENANTS_DATA:
            self.stdout.write(f'\n🏪 Creating tenant: {tenant_data["name"]}')
            
            tenant = Tenant(
                name=tenant_data['name'],
                slug=tenant_data['slug'],
                description=tenant_data['description'],
                cuisine_type=tenant_data['cuisine_type'],
                stall_number=tenant_data['stall_number'],
                banner_color=tenant_data['banner_color'],
                secondary_color=tenant_data['secondary_color'],
                icon_emoji=tenant_data['icon_emoji'],
                rating=tenant_data['rating'],
                total_orders=tenant_data['total_orders'],
                is_active=True,
                is_open=True,
            )
            
            # Assign logo
            slug = tenant_data['slug']
            if slug in tenant_logo_files:
                tenant.logo = tenant_logo_files[slug]
            
            tenant.save()
            
            # Create categories
            categories = {}
            for i, cat_name in enumerate(tenant_data['categories']):
                cat = Category.objects.create(
                    tenant=tenant,
                    name=cat_name,
                    order=i,
                )
                categories[cat_name] = cat
            
            # Get image key for this cuisine
            img_key = cuisine_to_img.get(tenant_data['cuisine_type'], 'ramen')
            img_content = product_image_files.get(img_key)
            
            # Assign categories to products
            cat_mapping = {
                'japanese': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 2, 7: 1, 8: 3, 9: 3},
                'korean': {0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 0, 6: 1, 7: 0, 8: 2, 9: 3},
                'italian': {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 3},
                'indonesian': {0: 0, 1: 0, 2: 1, 3: 2, 4: 1, 5: 1, 6: 1, 7: 1, 8: 3, 9: 3},
                'american': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 2, 8: 3, 9: 3},
                'thai': {0: 0, 1: 0, 2: 1, 3: 0, 4: 0, 5: 2, 6: 3, 7: 0, 8: 3, 9: 3},
                'chinese': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 2, 7: 1, 8: 3, 9: 3},
                'beverage': {0: 0, 1: 0, 2: 1, 3: 0, 4: 3, 5: 1, 6: 2, 7: 2, 8: 1, 9: 2},
                'mexican': {0: 0, 1: 1, 2: 0, 3: 2, 4: 0, 5: 2, 6: 0, 7: 2, 8: 3, 9: 3},
                'dessert': {0: 0, 1: 2, 2: 1, 3: 1, 4: 0, 5: 2, 6: 2, 7: 0, 8: 0, 9: 3},
            }
            
            cat_keys = list(categories.values())
            cat_map = cat_mapping.get(tenant_data['cuisine_type'], {})
            
            # Create products
            for idx, prod_data in enumerate(tenant_data['products']):
                cat_idx = cat_map.get(idx, 0)
                category = cat_keys[min(cat_idx, len(cat_keys)-1)] if cat_keys else None
                
                product = Product(
                    tenant=tenant,
                    category=category,
                    name=prod_data['name'],
                    description=prod_data['desc'],
                    price=prod_data['price'],
                    is_available=True,
                    is_featured=prod_data.get('featured', False),
                    is_bestseller=prod_data.get('best', False),
                    is_spicy=prod_data.get('spicy', False),
                    is_vegetarian=prod_data.get('veg', False),
                    preparation_time=prod_data.get('time', 10),
                    calories=prod_data.get('calories'),
                    order=idx,
                )
                
                # Assign product image
                if img_content:
                    product.image.save(
                        f'{slug}_{idx}_{prod_data["name"].replace(" ", "_")[:20]}.jpg',
                        ContentFile(img_content),
                        save=False
                    )
                
                product.save()
                self.stdout.write(f'  ✅ Product: {prod_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Seeding completed!'))
        self.stdout.write(f'🏪 Tenants: {Tenant.objects.count()}')
        self.stdout.write(f'📦 Products: {Product.objects.count()}')
        self.stdout.write(f'📂 Categories: {Category.objects.count()}')
