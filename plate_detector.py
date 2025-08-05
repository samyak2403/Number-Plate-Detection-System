import cv2
import numpy as np
import re
from PIL import Image
import time
import random

class NumberPlateDetector:
    def __init__(self):
        # Initialize cascade classifier for license plate detection
        self.plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')
        if self.plate_cascade.empty():
            # Fallback to frontal face cascade if plate cascade not available
            self.plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize contour-based detection parameters
        self.min_area = 500
        self.max_area = 50000
        
    def detect_plates(self, frame):
        """
        Detect number plates using multiple methods:
        1. Haar cascade classifier
        2. Contour detection with morphological operations
        3. Edge detection with rectangle finding
        """
        results = []
        
        # Method 1: Haar Cascade Detection
        cascade_results = self._detect_with_cascade(frame)
        results.extend(cascade_results)
        
        # Method 2: Contour-based detection
        contour_results = self._detect_with_contours(frame)
        results.extend(contour_results)
        
        # Method 3: Edge-based detection
        edge_results = self._detect_with_edges(frame)
        results.extend(edge_results)
        
        # Remove duplicate detections
        results = self._remove_duplicates(results)
        
        # Extract text from detected regions
        for result in results:
            x1, y1, x2, y2 = result['bbox']
            crop_img = frame[y1:y2, x1:x2]
            if crop_img.size > 0:
                result['text'] = self.extract_text(crop_img)
        
        return results
    
    def _detect_with_cascade(self, frame):
        """Detect plates using Haar cascade classifier"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(gray, 1.1, 4)
        
        results = []
        for (x, y, w, h) in plates:
            # Filter by aspect ratio (typical license plate ratio)
            aspect_ratio = w / h
            if 2.0 < aspect_ratio < 5.0 and w > 80 and h > 20:
                confidence = random.uniform(0.7, 0.95)  # Simulated confidence
                results.append({
                    'bbox': [x, y, x + w, y + h],
                    'confidence': confidence,
                    'method': 'cascade'
                })
        
        return results
    
    def _detect_with_contours(self, frame):
        """Detect plates using contour analysis"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Find edges
        edged = cv2.Canny(filtered, 30, 200)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        results = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area < area < self.max_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Check if it looks like a license plate
                if 2.0 < aspect_ratio < 5.0 and w > 80 and h > 20:
                    confidence = random.uniform(0.6, 0.85)  # Simulated confidence
                    results.append({
                        'bbox': [x, y, x + w, y + h],
                        'confidence': confidence,
                        'method': 'contour'
                    })
        
        return results
    
    def _detect_with_edges(self, frame):
        """Detect plates using edge detection and rectangle finding"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        results = []
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if contour has 4 points (rectangle-like)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / h
                area = cv2.contourArea(contour)
                
                if (2.0 < aspect_ratio < 5.0 and 
                    self.min_area < area < self.max_area and 
                    w > 80 and h > 20):
                    
                    confidence = random.uniform(0.65, 0.90)  # Simulated confidence
                    results.append({
                        'bbox': [x, y, x + w, y + h],
                        'confidence': confidence,
                        'method': 'edge'
                    })
        
        return results
    
    def _remove_duplicates(self, results):
        """Remove overlapping detections"""
        if not results:
            return results
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        filtered_results = []
        for result in results:
            is_duplicate = False
            x1, y1, x2, y2 = result['bbox']
            
            for existing in filtered_results:
                ex1, ey1, ex2, ey2 = existing['bbox']
                
                # Calculate overlap
                overlap_x = max(0, min(x2, ex2) - max(x1, ex1))
                overlap_y = max(0, min(y2, ey2) - max(y1, ey1))
                overlap_area = overlap_x * overlap_y
                
                area1 = (x2 - x1) * (y2 - y1)
                area2 = (ex2 - ex1) * (ey2 - ey1)
                
                # If overlap is more than 50%, consider it duplicate
                if overlap_area > 0.5 * min(area1, area2):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_results.append(result)
        
        return filtered_results
    
    def extract_text(self, image):
        """Extract text from license plate image using OCR simulation"""
        if image.size == 0:
            return ""
        
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply image processing for better OCR
            # Resize image for better recognition
            height, width = gray.shape
            if height < 50:
                scale_factor = 50 / height
                new_width = int(width * scale_factor)
                gray = cv2.resize(gray, (new_width, 50))
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Simulate OCR result (in real implementation, use pytesseract here)
            # For demo purposes, generate realistic Indian license plate numbers
            sample_plates = [
                "MH09AB1234", "DL01BC5678", "KA05MN9012", "TN07PQ3456",
                "GJ02RS7890", "RJ14UV2345", "UP16XY6789", "WB19CD0123",
                "MP04EF4567", "HR26GH8901", "PB03IJ2345", "AP28KL6789",
                "TS09MN0123", "KL08OP4567", "OR21QR8901", "JH20ST2345"
            ]
            
            # Return a random plate number (in real implementation, this would be OCR result)
            if random.random() > 0.3:  # 70% success rate simulation
                return random.choice(sample_plates)
            else:
                return ""  # Simulate OCR failure
                
        except Exception as e:
            print(f"Error in text extraction: {e}")
            return ""

