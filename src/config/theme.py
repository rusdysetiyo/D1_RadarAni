class ThemeManager:
    # 1. Sakura Matcha
    SAKURA_MATCHA = {
        "bg": "#FFF7F9", "bg_secondary": "#FFEBF0", "card": "#FFFFFF",
        "primary": "#D47793", "primary_light": "#FFD6E8",
        "text_main": "#4A2E35", "text_secondary": "#8D6E79", "text_muted": "#BFA5B0",
        "border_color": "#FFC4D4", "accent_star": "#F59E0B",
        "logo_1": "#FF759E", "logo_2": "#C3D3B4",
        "petal_colors": ["#FFB7C5", "#FFD1DC", "#F8A1B9"],
        "pill_rated": "#E65C7B", "pill_unrated": "#6B9B73", "pill_avg": "#D47793", "pill_top": "#C05C83",
        "banner_grad": ["#FFEBF0", "#FFFFFF", "#FFFFFF", "#FFEBF0"],
        "pill_text": "#3A1B24",
        "card_hover_border": "#FF759E",
        "overlay_bg": "#D9000000",
        "pill_genre_bg": "#FFC2D4",
        "overlay_text": "#FFD6E8",
        "success": "#10B981",
        "error": "#EF4444",
        "chart_colors": [ #buat di analytics and profile
            "#8C3057", "#C06080", "#E07AAA", "#F5B8D0", "#F3D8E8",
            "#D4A8C0", "#E8D0DE", "#A0506A", "#F0E4EB", "#B08090"
        ],
        "radar_grid": "#FFC4D4", #buat di halaman detail
        "radar_labels": "#8D6E79",
        "radar_p_border": "#E64A79",
        "radar_p_area": "#40E64A79",
        "radar_g_border": "#6B9B73",
        "radar_g_area": "#406B9B73",
        "stat_icon_bg": "#FFEBF0",
        "stat_gold": "#F59E0B"
    }

    # 2. Matcha Sakura
    MATCHA_SAKURA = {
        "bg": "#F5F7F2", "bg_secondary": "#E8ECE1", "card": "#FFFFFF",
        "primary": "#5C805C", "primary_light": "#C3D8C7",
        "text_main": "#4A5348", "text_secondary": "#7D8C78", "text_muted": "#A2B09E",
        "border_color": "#B5C7A3", "accent_star": "#D4B070",
        "pill_genre_bg": "#CDE0CD",
        "overlay_text": "#C3D8C7",
        "logo_1": "#C3D3B4", "logo_2": "#DDA7B0",
        "petal_colors": ["#DBE8D0", "#C3D3B4", "#E8CEDB"],
        "pill_rated": "#8BA870", "pill_unrated": "#DE7C88", "pill_avg": "#A4BA8C", "pill_top": "#75905D",
        "banner_grad": ["#E8ECE1", "#FFFFFF", "#FFFFFF", "#E8ECE1"],
        "pill_text": "#2D3B2D",
        "card_hover_border": "#96AB84", "overlay_bg": "#D9000000",
        "success": "#4CAF50",
        "error": "#E57373",
        "chart_colors": [
            "#4A7337", "#6A9955", "#8FB97B", "#B5D6A4", "#DBECC7",
            "#5C805C", "#7D8C78", "#96AB84", "#B5C7A3", "#CDE0CD"
        ],
        "radar_grid": "#B5C7A3",
        "radar_labels": "#7D8C78",
        "radar_p_border": "#5C805C",
        "radar_p_area": "#405C805C",
        "radar_g_border": "#DE7C88",
        "radar_g_area": "#40DE7C88",
        "stat_icon_bg": "#E8ECE1",
        "stat_gold": "#D4B070"
    }

    # 3. Dark Anime
    DARK_ANIME = {
        "bg": "#121212", "bg_secondary": "#1E1E1E", "card": "#1E1E1E",
        "primary": "#E8CEDB", "primary_light": "#2D3A2F",
        "text_main": "#F5F5F5", "text_secondary": "#B0B0B0", "text_muted": "#666666",
        "border_color": "#333333", "accent_star": "#FFD700",
        "pill_text": "#121212",
        "pill_genre_bg": "#E8CEDB",
        "overlay_text": "#F8F8F8",

        "logo_1": "#E8CEDB", "logo_2": "#C3D3B4",
        "petal_colors": ["#E8CEDB", "#C3D3B4", "#FFFFFF"],
        "pill_rated": "#DE7C88", "pill_unrated": "#84A381", "pill_avg": "#B88496", "pill_top": "#C0616D",
        "banner_grad": ["#1E1E1E", "#2A2A2A", "#2A2A2A", "#1E1E1E"],
        "card_hover_border": "#E8CEDB", "overlay_bg": "#E6000000",
        "success": "#81C784",
        "error": "#E53935",
        "chart_colors": [
            "#FF4D8D", "#FF7AA8", "#FFA6C4", "#FFD1E0", "#A8D592",
            "#C0616D", "#B88496", "#E8CEDB", "#84A381", "#DE7C88"
        ],
        "radar_grid": "#333333",
        "radar_labels": "#B0B0B0",
        "radar_p_border": "#E8CEDB",
        "radar_p_area": "#40E8CEDB",
        "radar_g_border": "#84A381",
        "radar_g_area": "#4084A381",
        "stat_icon_bg": "#2D3A2F",
        "stat_gold": "#FFD700"
    }

    # 4. Universal Clean
    UNIVERSAL_CLEAN = {
        "bg": "#F8F9FA", "bg_secondary": "#E9ECEF", "card": "#FFFFFF",
        "primary": "#3B82F6", "primary_light": "#DBEAFE",
        "text_main": "#1F2937", "text_secondary": "#6B7280", "text_muted": "#9CA3AF",
        "border_color": "#E5E7EB", "accent_star": "#F59E0B",
        "pill_text": "#FFFFFF",
        "pill_genre_bg": "#3B82F6",
        "overlay_text": "#DBEAFE",
        "logo_1": "#3B82F6", "logo_2": "#1D4ED8",
        "petal_colors": ["#DBEAFE", "#BFDBFE", "#93C5FD"],
        "pill_rated": "#10B981", "pill_unrated": "#3B82F6", "pill_avg": "#6366F1", "pill_top": "#8B5CF6",
        "banner_grad": ["#F8F9FA", "#FFFFFF", "#FFFFFF", "#F8F9FA"],
        "success": "#10B981",
        "error": "#EF4444",
        "card_hover_border": "#3B82F6", "overlay_bg": "#D9000000",
        "chart_colors": [
            "#1D4ED8", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD",
            "#1E3A8A", "#4F46E5", "#6366F1", "#8B5CF6", "#C4B5FD"
        ],
        "radar_grid": "#E5E7EB",
        "radar_labels": "#6B7280",
        "radar_p_border": "#3B82F6",
        "radar_p_area": "#403B82F6",
        "radar_g_border": "#8B5CF6",
        "radar_g_area": "#408B5CF6",
        "stat_icon_bg": "#DBEAFE",
        "stat_gold": "#F59E0B"
    }

    @staticmethod
    def get_theme(key):
        themes = {"1": ThemeManager.SAKURA_MATCHA, "2": ThemeManager.MATCHA_SAKURA, "3": ThemeManager.DARK_ANIME,
                  "4": ThemeManager.UNIVERSAL_CLEAN}
        return themes.get(key, ThemeManager.SAKURA_MATCHA)