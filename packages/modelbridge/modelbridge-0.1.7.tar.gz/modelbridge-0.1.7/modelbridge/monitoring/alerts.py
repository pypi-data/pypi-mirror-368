"""
Alert management and notification system
"""
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Alert instance"""
    name: str
    level: AlertLevel
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: AlertStatus = AlertStatus.ACTIVE
    details: Dict[str, Any] = field(default_factory=dict)
    count: int = 1
    first_seen: datetime = field(default=None)
    last_seen: datetime = field(default=None)
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = self.timestamp
        if self.last_seen is None:
            self.last_seen = self.timestamp
    
    @property
    def alert_id(self) -> str:
        """Unique alert identifier"""
        return f"{self.source}:{self.name}"
    
    @property
    def is_active(self) -> bool:
        """Check if alert is active"""
        return self.status == AlertStatus.ACTIVE
    
    @property
    def is_critical(self) -> bool:
        """Check if alert is critical"""
        return self.level == AlertLevel.CRITICAL
    
    @property
    def duration(self) -> timedelta:
        """Alert duration"""
        return self.last_seen - self.first_seen
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "details": self.details,
            "count": self.count,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "duration_seconds": self.duration.total_seconds()
        }


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    level: AlertLevel
    message_template: str
    source: str = "modelbridge"
    enabled: bool = True
    cooldown_seconds: int = 300  # 5 minutes default cooldown
    max_alerts_per_hour: int = 10
    
    # Thresholds
    threshold: Optional[float] = None
    comparison: str = ">"  # >, <, >=, <=, ==, !=
    
    def __post_init__(self):
        # Create condition function from threshold if provided
        if self.threshold is not None and not callable(self.condition):
            def threshold_condition(metrics: Dict[str, Any]) -> bool:
                # This is a simplified implementation
                # In practice, you'd extract the relevant metric value
                return False
            self.condition = threshold_condition


class AlertManager:
    """Alert manager for ModelBridge"""
    
    def __init__(self, max_alerts: int = 1000):
        self.max_alerts = max_alerts
        self._alerts: Dict[str, Alert] = {}
        self._rules: Dict[str, AlertRule] = {}
        self._alert_history: List[Alert] = []
        self._suppressed_alerts: Dict[str, datetime] = {}
        self._alert_counters: Dict[str, List[datetime]] = {}
        
        # Notification callbacks
        self._notification_handlers: List[Callable[[Alert], None]] = []
        
        # Register default rules
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register default alert rules"""
        # High error rate
        self.add_rule(AlertRule(
            name="high_error_rate",
            condition=lambda m: m.get("error_rate", 0) > 0.1,  # 10% error rate
            level=AlertLevel.ERROR,
            message_template="High error rate detected: {error_rate:.2%}",
            cooldown_seconds=300
        ))
        
        # High latency
        self.add_rule(AlertRule(
            name="high_latency",
            condition=lambda m: m.get("avg_latency", 0) > 5.0,  # 5 second average latency
            level=AlertLevel.WARNING,
            message_template="High average latency: {avg_latency:.2f}s",
            cooldown_seconds=300
        ))
        
        # Provider unhealthy
        self.add_rule(AlertRule(
            name="provider_unhealthy",
            condition=lambda m: len(m.get("unhealthy_providers", [])) > 0,
            level=AlertLevel.CRITICAL,
            message_template="Unhealthy providers: {unhealthy_providers}",
            cooldown_seconds=60
        ))
        
        # High cost
        self.add_rule(AlertRule(
            name="high_cost_per_request",
            condition=lambda m: m.get("avg_cost_per_request", 0) > 1.0,  # $1 per request
            level=AlertLevel.WARNING,
            message_template="High cost per request: ${avg_cost_per_request:.4f}",
            cooldown_seconds=600  # 10 minutes
        ))
        
        # Cache failure
        self.add_rule(AlertRule(
            name="cache_failure", 
            condition=lambda m: m.get("cache_error_rate", 0) > 0.05,  # 5% cache error rate
            level=AlertLevel.ERROR,
            message_template="Cache failures detected: {cache_error_rate:.2%}",
            cooldown_seconds=300
        ))
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self._rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.level.value})")
    
    def remove_rule(self, rule_name: str):
        """Remove an alert rule"""
        if rule_name in self._rules:
            del self._rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add a notification handler"""
        self._notification_handlers.append(handler)
        logger.info("Added notification handler")
    
    def evaluate_rules(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Evaluate all rules against current metrics"""
        new_alerts = []
        
        for rule_name, rule in self._rules.items():
            if not rule.enabled:
                continue
            
            try:
                # Check if rule is in cooldown
                if self._is_in_cooldown(rule_name):
                    continue
                
                # Check rate limiting
                if self._is_rate_limited(rule_name):
                    continue
                
                # Evaluate condition
                if rule.condition(metrics):
                    alert = self._create_alert_from_rule(rule, metrics)
                    new_alerts.append(alert)
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_name}: {e}")
        
        return new_alerts
    
    def fire_alert(self, alert: Alert) -> bool:
        """Fire an alert"""
        try:
            alert_id = alert.alert_id
            
            # Check if alert already exists
            if alert_id in self._alerts:
                existing = self._alerts[alert_id]
                existing.count += 1
                existing.last_seen = alert.timestamp
                alert = existing
            else:
                # New alert
                self._alerts[alert_id] = alert
                self._alert_history.append(alert)
                
                # Limit history size
                if len(self._alert_history) > self.max_alerts:
                    self._alert_history = self._alert_history[-self.max_alerts:]
            
            # Send notifications
            self._send_notifications(alert)
            
            # Update cooldown
            self._set_cooldown(alert.name)
            
            # Update rate limiting
            self._update_rate_counter(alert.name)
            
            logger.warning(f"Alert fired: {alert.name} ({alert.level.value}) - {alert.message}")
            return True
            
        except Exception as e:
            logger.error(f"Error firing alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, message: str = "") -> bool:
        """Resolve an active alert"""
        if alert_id in self._alerts:
            alert = self._alerts[alert_id]
            if alert.is_active:
                alert.status = AlertStatus.RESOLVED
                alert.last_seen = datetime.utcnow()
                if message:
                    alert.details["resolution_message"] = message
                
                logger.info(f"Alert resolved: {alert_id}")
                return True
        
        return False
    
    def suppress_alert(self, alert_id: str, duration_minutes: int = 60) -> bool:
        """Suppress an alert for a duration"""
        if alert_id in self._alerts:
            alert = self._alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            
            suppression_end = datetime.utcnow() + timedelta(minutes=duration_minutes)
            self._suppressed_alerts[alert_id] = suppression_end
            
            logger.info(f"Alert suppressed: {alert_id} for {duration_minutes} minutes")
            return True
        
        return False
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by level"""
        alerts = [alert for alert in self._alerts.values() if alert.is_active]
        
        if level:
            alerts = [alert for alert in alerts if alert.level == level]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            alert for alert in self._alert_history
            if alert.timestamp >= cutoff
        ]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        active_alerts = self.get_active_alerts()
        recent_alerts = self.get_alert_history(24)
        
        stats = {
            "total_active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.is_critical]),
            "alerts_last_24h": len(recent_alerts),
            "alert_breakdown": {},
            "top_sources": {}
        }
        
        # Alert breakdown by level
        for level in AlertLevel:
            count = len([a for a in active_alerts if a.level == level])
            if count > 0:
                stats["alert_breakdown"][level.value] = count
        
        # Top sources
        source_counts = {}
        for alert in recent_alerts:
            source_counts[alert.source] = source_counts.get(alert.source, 0) + 1
        
        stats["top_sources"] = dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return stats
    
    def _create_alert_from_rule(self, rule: AlertRule, metrics: Dict[str, Any]) -> Alert:
        """Create alert from rule and metrics"""
        # Format message template with metrics
        try:
            message = rule.message_template.format(**metrics)
        except (KeyError, ValueError):
            message = rule.message_template
        
        return Alert(
            name=rule.name,
            level=rule.level,
            message=message,
            source=rule.source,
            details={"metrics_snapshot": metrics}
        )
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if rule is in cooldown period"""
        if rule_name not in self._rules:
            return False
        
        rule = self._rules[rule_name]
        alert_id = f"{rule.source}:{rule_name}"
        
        if alert_id in self._alerts:
            last_alert = self._alerts[alert_id]
            cooldown_end = last_alert.last_seen + timedelta(seconds=rule.cooldown_seconds)
            return datetime.utcnow() < cooldown_end
        
        return False
    
    def _is_rate_limited(self, rule_name: str) -> bool:
        """Check if rule is rate limited"""
        if rule_name not in self._rules:
            return False
        
        rule = self._rules[rule_name]
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        if rule_name in self._alert_counters:
            # Clean old entries
            self._alert_counters[rule_name] = [
                timestamp for timestamp in self._alert_counters[rule_name]
                if timestamp > hour_ago
            ]
            
            # Check if we've hit the limit
            return len(self._alert_counters[rule_name]) >= rule.max_alerts_per_hour
        
        return False
    
    def _set_cooldown(self, rule_name: str):
        """Set cooldown for a rule"""
        # Cooldown is handled by checking last_seen time
        pass
    
    def _update_rate_counter(self, rule_name: str):
        """Update rate limiting counter"""
        if rule_name not in self._alert_counters:
            self._alert_counters[rule_name] = []
        
        self._alert_counters[rule_name].append(datetime.utcnow())
    
    def _send_notifications(self, alert: Alert):
        """Send alert notifications"""
        for handler in self._notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
    
    def cleanup_resolved_alerts(self, older_than_hours: int = 24):
        """Clean up old resolved alerts"""
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        alerts_to_remove = []
        for alert_id, alert in self._alerts.items():
            if (alert.status == AlertStatus.RESOLVED and 
                alert.last_seen < cutoff):
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self._alerts[alert_id]
        
        # Clean up suppressed alerts
        expired_suppressions = []
        for alert_id, suppression_end in self._suppressed_alerts.items():
            if datetime.utcnow() > suppression_end:
                expired_suppressions.append(alert_id)
        
        for alert_id in expired_suppressions:
            del self._suppressed_alerts[alert_id]
            if alert_id in self._alerts:
                self._alerts[alert_id].status = AlertStatus.ACTIVE
        
        if alerts_to_remove or expired_suppressions:
            logger.info(f"Cleaned up {len(alerts_to_remove)} resolved alerts and {len(expired_suppressions)} expired suppressions")


# Default notification handlers
def console_notification_handler(alert: Alert):
    """Simple console notification handler"""
    level_colors = {
        AlertLevel.INFO: "\033[94m",      # Blue
        AlertLevel.WARNING: "\033[93m",   # Yellow
        AlertLevel.ERROR: "\033[91m",     # Red
        AlertLevel.CRITICAL: "\033[95m",  # Magenta
    }
    
    color = level_colors.get(alert.level, "")
    reset = "\033[0m"
    
    print(f"{color}[ALERT {alert.level.value.upper()}]{reset} {alert.source}:{alert.name} - {alert.message}")


def log_notification_handler(alert: Alert):
    """Log-based notification handler"""
    log_levels = {
        AlertLevel.INFO: logging.INFO,
        AlertLevel.WARNING: logging.WARNING,
        AlertLevel.ERROR: logging.ERROR,
        AlertLevel.CRITICAL: logging.CRITICAL,
    }
    
    level = log_levels.get(alert.level, logging.INFO)
    logger.log(level, f"Alert: {alert.source}:{alert.name} - {alert.message}")


class WebhookNotificationHandler:
    """Webhook-based notification handler"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
    
    def __call__(self, alert: Alert):
        """Send alert via webhook"""
        import aiohttp
        import asyncio
        
        async def send_webhook():
            try:
                payload = {
                    "alert": alert.to_dict(),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.webhook_url,
                        json=payload,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status >= 400:
                            logger.error(f"Webhook notification failed: {response.status}")
                        else:
                            logger.debug(f"Webhook notification sent for alert: {alert.alert_id}")
                            
            except Exception as e:
                logger.error(f"Error sending webhook notification: {e}")
        
        # Run webhook in background
        try:
            asyncio.create_task(send_webhook())
        except RuntimeError:
            # No event loop running, skip webhook
            logger.warning("No event loop available for webhook notification")


class SlackNotificationHandler:
    """Slack notification handler"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.level_colors = {
            AlertLevel.INFO: "#36a64f",      # Green
            AlertLevel.WARNING: "#ff9500",   # Orange
            AlertLevel.ERROR: "#ff0000",     # Red
            AlertLevel.CRITICAL: "#800080",  # Purple
        }
    
    def __call__(self, alert: Alert):
        """Send alert to Slack"""
        import aiohttp
        import asyncio
        
        async def send_slack():
            try:
                color = self.level_colors.get(alert.level, "#cccccc")
                
                payload = {
                    "attachments": [{
                        "color": color,
                        "title": f"ModelBridge Alert: {alert.name}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Level", "value": alert.level.value.upper(), "short": True},
                            {"title": "Source", "value": alert.source, "short": True},
                            {"title": "Count", "value": str(alert.count), "short": True},
                            {"title": "Duration", "value": f"{alert.duration.total_seconds():.0f}s", "short": True}
                        ],
                        "timestamp": alert.timestamp.isoformat()
                    }]
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.webhook_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status >= 400:
                            logger.error(f"Slack notification failed: {response.status}")
                        else:
                            logger.debug(f"Slack notification sent for alert: {alert.alert_id}")
                            
            except Exception as e:
                logger.error(f"Error sending Slack notification: {e}")
        
        try:
            asyncio.create_task(send_slack())
        except RuntimeError:
            logger.warning("No event loop available for Slack notification")