"""
Improved Enderman GitHub Contribution Animation Generator
Enhanced version with better Enderman sprite and teleportation effects
"""

import requests
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
import argparse
import random

class ImprovedEndermanAnimation:
    def __init__(self, username, output_path="enderman-animation.gif"):
        self.username = username
        self.output_path = output_path
        self.cell_size = 15
        self.gap = 2
        self.enderman_color = (20, 20, 20)  # Dark gray for Enderman body
        self.enderman_eyes = (255, 0, 255)  # Purple eyes
        self.teleport_particles = (138, 43, 226)  # Purple particles
        self.contribution_colors = [
            (22, 27, 34),     # No contributions (dark)
            (14, 68, 41),     # Low (dark green)
            (0, 109, 50),     # Medium-low (green)
            (38, 166, 65),    # Medium (bright green)
            (57, 211, 83)     # High (very bright green)
        ]
        
    def fetch_contributions(self):
        """Fetch GitHub contribution data"""
        # Generate more realistic sample data
        contributions = []
        
        # Generate a year's worth of sample data with patterns
        start_date = datetime.now() - timedelta(days=365)
        for i in range(365):
            date = start_date + timedelta(days=i)
            
            # Create patterns: more activity on weekdays, less on weekends
            day_of_week = date.weekday()
            if day_of_week < 5:  # Weekday
                count = np.random.choice([0, 1, 2, 3, 4, 5, 8, 12], p=[0.1, 0.2, 0.25, 0.2, 0.15, 0.05, 0.03, 0.02])
            else:  # Weekend
                count = np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1])
            
            # Convert count to GitHub level (0-4)
            if count == 0:
                level = 0
            elif count <= 2:
                level = 1
            elif count <= 5:
                level = 2
            elif count <= 8:
                level = 3
            else:
                level = 4
                
            contributions.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count,
                'level': level
            })
        
        return contributions
    
    def create_grid(self, contributions):
        """Create the contribution grid layout"""
        # GitHub shows 53 weeks (columns) x 7 days (rows)
        grid = np.zeros((7, 53), dtype=int)
        
        # Fill the grid with contribution data
        for i, contrib in enumerate(contributions[-371:]):  # Last 53 weeks
            week = i // 7
            day = i % 7
            if week < 53:
                grid[day][week] = contrib['level']
        
        return grid
    
    def create_enderman_sprite(self, size=20, frame=0):
        """Create an animated Enderman sprite with teleportation effects"""
        sprite = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sprite)
        
        # Animation offset for slight movement
        offset = int(np.sin(frame * 0.3) * 1)
        
        # Enderman head (larger and more detailed)
        head_size = size // 2
        head_x = size // 4
        head_y = offset
        draw.rectangle([head_x, head_y, head_x + head_size, head_y + head_size], 
                      fill=self.enderman_color, outline=(40, 40, 40))
        
        # Eyes (glowing purple)
        eye_size = size // 10
        eye_y = head_y + size // 8
        # Left eye
        draw.rectangle([head_x + size//8, eye_y, head_x + size//8 + eye_size, eye_y + eye_size], 
                      fill=self.enderman_eyes)
        # Right eye
        draw.rectangle([head_x + 3*size//8, eye_y, head_x + 3*size//8 + eye_size, eye_y + eye_size], 
                      fill=self.enderman_eyes)
        
        # Body (tall and thin)
        body_width = size // 3
        body_height = size // 2
        body_x = size // 3
        body_y = head_y + head_size
        draw.rectangle([body_x, body_y, body_x + body_width, body_y + body_height], 
                      fill=self.enderman_color, outline=(40, 40, 40))
        
        # Long arms
        arm_width = size // 12
        arm_length = size // 2
        # Left arm
        draw.rectangle([body_x - arm_width, body_y, body_x, body_y + arm_length], 
                      fill=self.enderman_color)
        # Right arm
        draw.rectangle([body_x + body_width, body_y, body_x + body_width + arm_width, body_y + arm_length], 
                      fill=self.enderman_color)
        
        # Long legs
        leg_width = size // 12
        leg_length = size // 4
        leg_y = body_y + body_height
        # Left leg
        draw.rectangle([body_x + size//12, leg_y, body_x + size//12 + leg_width, leg_y + leg_length], 
                      fill=self.enderman_color)
        # Right leg
        draw.rectangle([body_x + size//4, leg_y, body_x + size//4 + leg_width, leg_y + leg_length], 
                      fill=self.enderman_color)
        
        return sprite
    
    def create_teleport_effect(self, size=20, intensity=1.0):
        """Create purple particle effect for teleportation"""
        effect = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(effect)
        
        # Random purple particles
        for _ in range(int(10 * intensity)):
            x = random.randint(0, size-2)
            y = random.randint(0, size-2)
            particle_size = random.randint(1, 3)
            alpha = int(255 * intensity * random.random())
            color = (*self.teleport_particles, alpha)
            draw.rectangle([x, y, x + particle_size, y + particle_size], fill=color)
        
        return effect
    
    def generate_path(self, grid):
        """Generate a more interesting path for the Enderman"""
        rows, cols = grid.shape
        path = []
        
        # Collect all cells with contributions
        contribution_cells = []
        for row in range(rows):
            for col in range(cols):
                if grid[row][col] > 0:
                    contribution_cells.append((row, col, grid[row][col]))
        
        # Sort by contribution level (highest first) and add some randomness
        contribution_cells.sort(key=lambda x: (x[2], random.random()), reverse=True)
        
        # Create path - Enderman prefers high-contribution cells
        path = [(row, col) for row, col, level in contribution_cells]
        
        return path
    
    def create_frame(self, grid, enderman_pos, eaten_positions, frame_num, teleporting=False):
        """Create a single frame of the animation with enhanced effects"""
        rows, cols = grid.shape
        
        # Calculate image dimensions with padding
        padding = 20
        img_width = cols * (self.cell_size + self.gap) - self.gap + 2 * padding
        img_height = rows * (self.cell_size + self.gap) - self.gap + 2 * padding
        
        # Create image with GitHub-like dark background
        img = Image.new('RGB', (img_width, img_height), (13, 17, 23))
        draw = ImageDraw.Draw(img)
        
        # Draw contribution grid
        for row in range(rows):
            for col in range(cols):
                x = col * (self.cell_size + self.gap) + padding
                y = row * (self.cell_size + self.gap) + padding
                
                # Determine cell color and effects
                if (row, col) in eaten_positions:
                    # Eaten cells become darker with purple glow
                    color = (30, 20, 40)
                    # Add subtle purple glow
                    glow_color = (60, 20, 80)
                    draw.rectangle([x-1, y-1, x + self.cell_size + 1, y + self.cell_size + 1], 
                                 fill=glow_color, outline=glow_color)
                else:
                    level = grid[row][col]
                    color = self.contribution_colors[level]
                
                # Draw cell with rounded corners effect
                draw.rectangle([x, y, x + self.cell_size, y + self.cell_size], 
                             fill=color, outline=(30, 30, 30))
        
        # Draw Enderman with effects
        if enderman_pos:
            row, col = enderman_pos
            x = col * (self.cell_size + self.gap) + padding
            y = row * (self.cell_size + self.gap) + padding
            
            # Teleportation effect
            if teleporting:
                teleport_effect = self.create_teleport_effect(self.cell_size + 10, 0.8)
                img.paste(teleport_effect, (x-5, y-5), teleport_effect)
            
            # Create and paste Enderman sprite
            enderman_sprite = self.create_enderman_sprite(self.cell_size + 5, frame_num)
            img.paste(enderman_sprite, (x-2, y-2), enderman_sprite)
        
        # Add title
        try:
            # Try to use a font, fallback to default if not available
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        #title = f"Enderman roubando commits de {self.username}"
        #text_bbox = draw.textbbox((0, 0), title, font=font)
        #text_width = text_bbox[2] - text_bbox[0]
        #text_x = (img_width - text_width) // 2
        #draw.text((text_x, 5), title, fill=(255, 255, 255), font=font)
        
        return img
    
    def generate_animation(self):
        """Generate the complete animation with enhanced effects"""
        print(f"Fetching contributions for {self.username}...")
        contributions = self.fetch_contributions()
        
        print("Creating contribution grid...")
        grid = self.create_grid(contributions)
        
        print("Generating Enderman path...")
        path = self.generate_path(grid)
        
        print("Creating animation frames...")
        frames = []
        eaten_positions = set()
        
        # Create frames with teleportation effects
        for i in range(len(path) + 20):  # Extra frames at the end
            teleporting = False
            
            if i < len(path):
                current_pos = path[i]
                eaten_positions.add(current_pos)
                
                # Add teleportation effect every few moves
                if i > 0 and i % 5 == 0:
                    teleporting = True
            else:
                current_pos = None
            
            frame = self.create_frame(grid, current_pos, eaten_positions, i, teleporting)
            frames.append(frame)
            
            # Add extra teleport effect frames
            if teleporting and current_pos:
                for j in range(2):
                    effect_frame = self.create_frame(grid, current_pos, eaten_positions, i + j, True)
                    frames.append(effect_frame)
        
        # Save as GIF with optimized settings
        print(f"Saving animation to {self.output_path}...")
        frames[0].save(
            self.output_path,
            save_all=True,
            append_images=frames[1:],
            duration=150,  # 150ms per frame for smoother animation
            loop=0,
            optimize=True
        )
        
        print(f"Animation saved successfully!")
        print(f"Total frames: {len(frames)}")
        print(f"File size: {os.path.getsize(self.output_path) / 1024:.1f} KB")
        return self.output_path

def main():
    parser = argparse.ArgumentParser(description='Generate improved Enderman GitHub contribution animation')
    parser.add_argument('username', help='GitHub username')
    parser.add_argument('-o', '--output', default='enderman-animation.gif', 
                       help='Output file path (default: enderman-animation.gif)')
    
    args = parser.parse_args()
    
    animator = ImprovedEndermanAnimation(args.username, args.output)
    animator.generate_animation()

if __name__ == "__main__":
    main()

