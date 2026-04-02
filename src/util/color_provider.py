import colorsys

class ColorProvider:
    def __init__(self):
        self.hue_step = 0.618033988749895
        self.current_hue = 0.1           
        self.color_map = {}

    def generate_color_map(self, sample_names):
        h = self.current_hue

        for name in sample_names:
            h = (h + self.hue_step) % 1.0
            s = 0.7 
            v = 0.9 

            rgb = colorsys.hsv_to_rgb(h, s, v)
            hex_color = '#%02x%02x%02x' % tuple(int(x * 255) for x in rgb)
            self.color_map[name] = hex_color
        

        self.current_hue = h

        return self.color_map
    
    def get_color_map(self):
        return self.color_map