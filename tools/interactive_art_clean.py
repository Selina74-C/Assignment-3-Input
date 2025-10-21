"""Clean interactive generative artwork (Python + Pygame).

This is a self-contained script that reads a WAV (prefers
visual_garden/romantic_smooth.wav), computes running RMS in a background
thread, and renders an audio-reactive particle field with two sliders:
(sensitivity, smoothing).

Run: python tools/interactive_art_clean.py --duration 5
"""

import argparse
import threading
import time
from collections import deque
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import pygame


def audio_rms_stream(path, out_list, stop_event):
    data, sr = sf.read(str(path))
    if data.ndim > 1:
        data = data.mean(axis=1)
    """Clean interactive generative artwork (Python + Pygame).

    This is a self-contained script that reads a WAV (prefers
    visual_garden/romantic_smooth.wav), computes running RMS in a background
    thread, and renders an audio-reactive particle field with two sliders:
    (sensitivity, smoothing).

    Run: python tools/interactive_art_clean.py --duration 5
    """

    import argparse
    import threading
    import time
    from collections import deque
    from pathlib import Path
    import numpy as np
    import sounddevice as sd
    import soundfile as sf
    import pygame


    def audio_rms_stream(path, out_list, stop_event):
        data, sr = sf.read(str(path))
        if data.ndim > 1:
            data = data.mean(axis=1)
        pos = 0
        block = 1024
        while not stop_event.is_set() and pos < len(data):
            chunk = data[pos:pos + block]
            pos += block
            if len(chunk) == 0:
                rms = 0.0
            else:
                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
            out_list.append(rms)
            time.sleep(block / float(sr))


    class Slider:
        def __init__(self, rect, minv, maxv, value):
            self.rect = pygame.Rect(rect)
            self.minv = minv
            self.maxv = maxv
            self.value = value
            self.drag = False

        def handle_event(self, e):
            if e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
                self.drag = True
                self.set_from_pos(e.pos[0])
            elif e.type == pygame.MOUSEBUTTONUP:
                self.drag = False
            elif e.type == pygame.MOUSEMOTION and self.drag:
                self.set_from_pos(e.pos[0])

        def set_from_pos(self, x):
            rel = (x - self.rect.x) / float(self.rect.w)
            rel = max(0.0, min(1.0, rel))
            self.value = self.minv + rel * (self.maxv - self.minv)

        def draw(self, surf):
            pygame.draw.rect(surf, (50, 50, 60), self.rect)
            rel = (self.value - self.minv) / (self.maxv - self.minv)
            kx = int(self.rect.x + rel * self.rect.w)
            ky = self.rect.centery
            pygame.draw.circle(surf, (180, 220, 255), (kx, ky), 8)


    def play_audio(path):
        try:
            data, sr = sf.read(str(path))
            if data.ndim > 1:
                data = data.mean(axis=1)
            sd.stop()
            sd.play(data, sr)
            return data, sr
        except Exception:
            return None, None


    def main(duration=None):
        pygame.init()
        W, H = 1100, 640
        screen = pygame.display.set_mode((W, H))
        print("[DEBUG] Pygame window created.")
        import time as _dbg_time
        print("[DEBUG] Sleeping for 10 seconds after window creation...")
        _dbg_time.sleep(10)
        print("[DEBUG] Awake. Entering main event loop.")
        pygame.display.set_caption('Interactive Art')
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 32)
        input_active = False
        user_text = ''
        poetry_color = (255, 255, 255)

        orig = Path('romantic.wav')
        smooth = Path('visual_garden/romantic_smooth.wav')
        current = smooth if smooth.exists() else orig
        if not current.exists():
            print('Place romantic.wav or visual_garden/romantic_smooth.wav in the repo')
            return

        rms_list = []
        stop_event = threading.Event()
        t = threading.Thread(target=audio_rms_stream, args=(current, rms_list, stop_event), daemon=True)
        t.start()

        sens = Slider((20, H - 80, 300, 28), 0.5, 8.0, 3.0)
        smooth_s = Slider((360, H - 80, 300, 28), 0.0, 0.95, 0.4)

        particles = []
        data, sr = play_audio(current)
        playing = data is not None

        start = time.time()

        def spawn(x, y, rms, strength=1.0):
            n = int(1 + rms * 60 * sens.value * strength)
            for _ in range(max(1, n)):
                particles.append({
                    'x': x + np.random.uniform(-6, 6),
                    'y': y + np.random.uniform(-6, 6),
                    'vx': np.random.normal(0, 1) * (1 + rms * 4),
                    # bias initial vy upward by taking negative absolute value
                    'vy': -abs(np.random.normal(0, 1)) * (1 + rms * 4),
                    'life': np.random.randint(40, 180),
                    'col': (int(160 + np.random.uniform(0, 95)), int(180 + np.random.uniform(0, 60)), 255),
                })

        rms_deque = deque(maxlen=8)

        print("[DEBUG] Entering main event loop.")
        loop_count = 0
        while True:
            loop_count += 1
            if loop_count % 60 == 0:
                print(f"[DEBUG] Main loop iteration: {loop_count}")
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    stop_event.set(); sd.stop(); pygame.quit(); return
                if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    sens.handle_event(e); smooth_s.handle_event(e)
                if e.type == pygame.MOUSEMOTION:
                    x, y = e.pos; r = rms_list[-1] if rms_list else 0.0; spawn(x, y, r)
                if e.type == pygame.MOUSEBUTTONDOWN:
                    x, y = e.pos; r = rms_list[-1] if rms_list else 0.0; spawn(x, y, r * 2.0)
                if e.type == pygame.KEYDOWN:
                    if input_active:
                        if e.key == pygame.K_RETURN:
                            input_active = False
                            # Change background color based on text
                            poetry_color = tuple((hash(user_text + str(i)) % 200 + 55) for i in range(3))
                        elif e.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
                        else:
                            if e.unicode.isprintable():
                                user_text += e.unicode
                    else:
                        if e.key == pygame.K_t:
                            input_active = True
                            user_text = ''
                        if e.key == pygame.K_SPACE:
                            if playing: sd.stop(); playing = False
                            else: data and sd.play(data, sr); playing = True
                        if e.key == pygame.K_ESCAPE:
                            stop_event.set(); sd.stop(); pygame.quit(); return

            raw = rms_list[-1] if rms_list else 0.0
            sm = smooth_s.value
            display = raw if not rms_deque else sm * raw + (1 - sm) * rms_deque[-1]
            rms_deque.append(display)
            rms = display

            base = int(8 + min(120, rms * 3000))
            # Use poetry_color for background if text entered
            bg_color = poetry_color if user_text else (base, max(0, base // 2), int(base * 1.1) % 255)
            screen.fill(bg_color)

            for p in particles[:]:
                p['x'] += p['vx'] * 0.15; p['y'] += p['vy'] * 0.15; p['vy'] += 0.06; p['life'] -= 1
                a = max(0, min(255, int(255 * (p['life'] / 180))))
                surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(surf, (p['col'][0], p['col'][1], p['col'][2], a), (3, 3), 3)
                screen.blit(surf, (int(p['x']), int(p['y'])))
                if p['life'] <= 0: particles.remove(p)

            halo = 60 + rms * 360
            halo_surf = pygame.Surface((int(halo * 2), int(halo * 2)), pygame.SRCALPHA)
            pygame.draw.circle(halo_surf, (80, 160, 255, int(30 + rms * 200)), (int(halo), int(halo)), int(halo))
            screen.blit(halo_surf, (int(W / 2 - halo), int(H / 2 - halo)), special_flags=pygame.BLEND_ADD)

            pygame.draw.rect(screen, (200, 200, 200), (20, H - 110, 660, 38), 2)
            font_small = pygame.font.SysFont(None, 20)
            screen.blit(font_small.render('Sensitivity', True, (220, 220, 220)), (20, H - 140))
            sens.draw(screen)
            screen.blit(font_small.render('Smoothing', True, (220, 220, 220)), (360, H - 140))
            smooth_s.draw(screen)

            status = f'RMS={rms:.5f}  Sens={sens.value:.2f}  Smooth={smooth_s.value:.2f}'
            screen.blit(font_small.render(status, True, (220, 220, 220)), (20, 12))

            # Draw text input box if active
            if input_active:
                pygame.draw.rect(screen, (40, 40, 60), (W//2-200, H//2-30, 400, 40))
                pygame.draw.rect(screen, (200, 200, 255), (W//2-200, H//2-30, 400, 40), 2)
                txt = font.render(user_text, True, (220, 220, 255))
                screen.blit(txt, (W//2-190, H//2-22))
                screen.blit(font_small.render('Type and press Enter', True, (180,180,180)), (W//2-190, H//2+20))
            elif user_text:
                # Display the entered word as poetry
                txt = font.render(user_text, True, (poetry_color))
                screen.blit(txt, (W//2-190, H//2-22))

            pygame.display.flip(); clock.tick(60)

            if duration and (time.time() - start) > duration:
                stop_event.set(); sd.stop(); pygame.quit(); return


    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--duration', type=float, default=None)
        args = parser.parse_args()
        main(duration=args.duration)
