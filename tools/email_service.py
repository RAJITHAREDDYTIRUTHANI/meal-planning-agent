"""
Email Service for sending shopping lists and meal plans
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from observability.logger import get_logger

logger = get_logger("email_service")


class EmailService:
    """Service for sending emails with shopping lists and meal plans"""
    
    def __init__(self):
        """Initialize email service"""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self._check_configuration()
    
    def _check_configuration(self):
        """Check if email service is configured"""
        # Reload environment variables in case .env was updated
        from dotenv import load_dotenv
        load_dotenv()
        
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.enabled = bool(self.sender_email and self.sender_password)
        
        if not self.enabled:
            logger.debug(f"Email config check - SENDER_EMAIL: {'SET' if self.sender_email else 'NOT SET'}, SENDER_PASSWORD: {'SET' if self.sender_password else 'NOT SET'}")
    
    def send_shopping_list(
        self,
        recipient_email: str,
        shopping_list: Dict[str, Any],
        meal_plan: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send shopping list via email.
        
        Args:
            recipient_email: Recipient email address
            shopping_list: Shopping list data
            meal_plan: Optional meal plan data
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Re-check configuration in case .env was updated
        self._check_configuration()
        
        if not self.enabled:
            logger.warning("Email service not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in .env")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "Your Shopping List - Meal Planning Assistant"
            
            # Create email body
            body = self._format_shopping_list_email(shopping_list, meal_plan)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Shopping list sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _format_shopping_list_email(
        self,
        shopping_list: Dict[str, Any],
        meal_plan: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format shopping list as HTML email"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .section { margin: 20px 0; }
                .section-title { font-size: 1.5em; color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
                .item-list { list-style: none; padding: 0; }
                .item-list li { padding: 8px; background: #f7fafc; margin: 5px 0; border-left: 3px solid #667eea; }
                .total { font-size: 1.2em; font-weight: bold; color: #48bb78; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛒 Your Shopping List</h1>
            </div>
            <div class="content">
        """
        
        # Add meal plan summary if available
        if meal_plan:
            html += f"""
            <div class="section">
                <h2 class="section-title">📋 Meal Plan Summary</h2>
                <p><strong>Days:</strong> {meal_plan.get('days', 'N/A')}</p>
                <p><strong>Total Meals:</strong> {len(meal_plan.get('meals', []))}</p>
            </div>
            """
        
        # Add shopping list items
        if shopping_list.get("grouped_by_section"):
            html += '<div class="section"><h2 class="section-title">🛒 Shopping Items</h2>'
            for section, items in shopping_list["grouped_by_section"].items():
                html += f'<h3>{section.upper()}</h3><ul class="item-list">'
                for item in items:
                    html += f'<li>✓ {item}</li>'
                html += '</ul>'
            html += '</div>'
        
        # Add cost estimate
        if shopping_list.get("estimated_cost"):
            cost = shopping_list["estimated_cost"]
            total = cost.get('total_estimate', 0)
            html += f'<div class="total">💰 Total Estimated Cost: ${total:.2f}</div>'
        
        html += """
            </div>
        </body>
        </html>
        """
        return html

