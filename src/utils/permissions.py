# src/utils/permissions.py
from enum import Enum
from typing import List, Dict, Any
from .logger import logger

class Permission(Enum):
    # Permisos de usuarios
    USER_CREATE = "user_create"
    USER_EDIT = "user_edit"
    USER_DELETE = "user_delete"
    USER_VIEW_LOGS = "user_view_logs"
    USER_VIEW_ALL = "user_view_all"
    
    # Permisos de habitaciones
    ROOM_VIEW = "room_view"
    ROOM_CREATE = "room_create"
    ROOM_EDIT = "room_edit"
    ROOM_DELETE = "room_delete"
    ROOM_MAINTENANCE = "room_maintenance"
    ROOM_CHANGE_RATES = "room_change_rates"
    ROOM_VIEW_ALL = "room_view_all"
    
    # Permisos de tarifas
    RATE_VIEW = "rate_view"
    RATE_EDIT = "rate_edit"
    RATE_CREATE_SEASON = "rate_create_season"
    RATE_DELETE_SEASON = "rate_delete_season"
    
    # Permisos de reportes
    REPORT_VIEW_FINANCIAL = "report_view_financial"
    REPORT_VIEW_BASIC = "report_view_basic"
    REPORT_EXPORT = "report_export"
    REPORT_VIEW_PROFITABILITY = "report_view_profitability"
    REPORT_VIEW_ALL = "report_view_all"
    
    # Permisos de reservas
    BOOKING_CREATE = "booking_create"
    BOOKING_EDIT = "booking_edit"
    BOOKING_CANCEL = "booking_cancel"
    BOOKING_CANCEL_REFUND = "booking_cancel_refund"
    BOOKING_MODIFY_PRICE = "booking_modify_price"
    BOOKING_VIEW_ALL = "booking_view_all"
    BOOKING_VIEW_OWN = "booking_view_own"
    
    # Permisos de facturación
    INVOICE_VIEW = "invoice_view"
    INVOICE_VIEW_ALL = "invoice_view_all"
    INVOICE_CREATE = "invoice_create"
    INVOICE_VOID = "invoice_void"
    INVOICE_DISCOUNT = "invoice_discount"
    INVOICE_DISCOUNT_HIGH = "invoice_discount_high"  # >20%
    INVOICE_REFUND = "invoice_refund"
    
    # Permisos de configuración
    CONFIG_VIEW = "config_view"
    CONFIG_EDIT = "config_edit"
    BACKUP_CREATE = "backup_create"
    BACKUP_RESTORE = "backup_restore"
    
    # Permisos de dashboard
    DASHBOARD_VIEW = "dashboard_view"
    DASHBOARD_VIEW_KPI_ALL = "dashboard_view_kpi_all"
    DASHBOARD_VIEW_KPI_BASIC = "dashboard_view_kpi_basic"

class RoleManager:
    """Gestiona permisos por rol"""
    
    # Definición de permisos por rol - VERSIÓN CORREGIDA
    ROLE_PERMISSIONS = {
        'admin': [
            # Usuarios - todos los permisos
            Permission.USER_CREATE, Permission.USER_EDIT, 
            Permission.USER_DELETE, Permission.USER_VIEW_LOGS,
            Permission.USER_VIEW_ALL,
            
            # Habitaciones - todos
            Permission.ROOM_VIEW, Permission.ROOM_CREATE, 
            Permission.ROOM_EDIT, Permission.ROOM_DELETE,
            Permission.ROOM_MAINTENANCE, Permission.ROOM_CHANGE_RATES,
            Permission.ROOM_VIEW_ALL,
            
            # Tarifas - todos
            Permission.RATE_VIEW, Permission.RATE_EDIT, 
            Permission.RATE_CREATE_SEASON, Permission.RATE_DELETE_SEASON,
            
            # Reportes - todos
            Permission.REPORT_VIEW_FINANCIAL, Permission.REPORT_VIEW_BASIC,
            Permission.REPORT_EXPORT, Permission.REPORT_VIEW_PROFITABILITY,
            Permission.REPORT_VIEW_ALL,
            
            # Reservas - todos
            Permission.BOOKING_CREATE, Permission.BOOKING_EDIT,
            Permission.BOOKING_CANCEL, Permission.BOOKING_CANCEL_REFUND,
            Permission.BOOKING_MODIFY_PRICE, Permission.BOOKING_VIEW_ALL,
            Permission.BOOKING_VIEW_OWN,
            
            # Facturación - todos
            Permission.INVOICE_VIEW, Permission.INVOICE_VIEW_ALL,
            Permission.INVOICE_CREATE, Permission.INVOICE_VOID, 
            Permission.INVOICE_DISCOUNT, Permission.INVOICE_DISCOUNT_HIGH,
            Permission.INVOICE_REFUND,
            
            # Configuración - todos
            Permission.CONFIG_VIEW, Permission.CONFIG_EDIT,
            Permission.BACKUP_CREATE, Permission.BACKUP_RESTORE,
            
            # Dashboard - todos
            Permission.DASHBOARD_VIEW, Permission.DASHBOARD_VIEW_KPI_ALL,
            Permission.DASHBOARD_VIEW_KPI_BASIC
        ],
        
        'gerente': [
            # 👥 Usuarios - solo ver logs, NO ver lista completa
            Permission.USER_VIEW_LOGS,
            Permission.USER_CREATE,      # ✅ PUEDE registrar huéspedes
            # ❌ NO tiene USER_EDIT
            # ❌ NO tiene USER_DELETE
            # ❌ NO tiene USER_VIEW_ALL  (no ve lista de usuarios)
            
            # 🛏️ Habitaciones - puede gestionar pero no eliminar
            Permission.ROOM_VIEW, 
            Permission.ROOM_CREATE,  # Puede crear
            Permission.ROOM_EDIT,     # Puede editar
            # NO tiene ROOM_DELETE
            Permission.ROOM_MAINTENANCE, 
            Permission.ROOM_CHANGE_RATES,  # Con límite en controlador
            Permission.ROOM_VIEW_ALL,
            
            # 💰 Tarifas - puede ver y crear temporadas
            Permission.RATE_VIEW,
            Permission.RATE_CREATE_SEASON,  # Puede crear temporadas
            # NO tiene RATE_EDIT (factores base)
            # NO tiene RATE_DELETE_SEASON
            
            # 📊 Reportes - TODOS los reportes financieros
            Permission.REPORT_VIEW_FINANCIAL, 
            Permission.REPORT_VIEW_BASIC,
            Permission.REPORT_EXPORT, 
            Permission.REPORT_VIEW_PROFITABILITY,
            Permission.REPORT_VIEW_ALL,
            
            # 📝 Reservas - todos excepto modificar precios sin límite
            Permission.BOOKING_CREATE, Permission.BOOKING_EDIT,
            Permission.BOOKING_CANCEL, 
            Permission.BOOKING_CANCEL_REFUND,  # Con límite
            # NO tiene BOOKING_MODIFY_PRICE (o con límite del 10%)
            Permission.BOOKING_VIEW_ALL,
            Permission.BOOKING_VIEW_OWN,
            
            # 🧾 Facturación - no puede anular, descuentos limitados
            Permission.INVOICE_VIEW, 
            Permission.INVOICE_VIEW_ALL,
            Permission.INVOICE_CREATE,
            # NO tiene INVOICE_VOID
            Permission.INVOICE_DISCOUNT,  # Hasta 20%
            # NO tiene INVOICE_DISCOUNT_HIGH (>20%)
            # NO tiene INVOICE_REFUND
            
            # ⚙️ CONFIGURACIÓN - NINGUNO (CORREGIDO)
            # ❌ NO tiene CONFIG_VIEW
            # NO tiene CONFIG_EDIT
            # NO tiene BACKUP_CREATE
            # NO tiene BACKUP_RESTORE
            
            # 📈 Dashboard - KPIs completos (ve ingresos, RevPAR)
            Permission.DASHBOARD_VIEW, 
            Permission.DASHBOARD_VIEW_KPI_ALL,
            Permission.DASHBOARD_VIEW_KPI_BASIC
        ],
        
        'recepcionista': [
            # 👥 Usuarios - PUEDE REGISTRAR HUÉSPEDES (NUEVO)
            Permission.USER_CREATE,      # ✅ Puede registrar nuevos huéspedes
            # ❌ NO tiene USER_EDIT
            # ❌ NO tiene USER_DELETE
            # ❌ NO tiene USER_VIEW_ALL
            # ❌ NO tiene USER_VIEW_LOGS
            
            # 🛏️ Habitaciones - solo ver
            Permission.ROOM_VIEW,
            Permission.ROOM_VIEW_ALL,
            # NO tiene ROOM_CREATE, ROOM_EDIT, ROOM_DELETE
            # NO tiene ROOM_MAINTENANCE
            # NO tiene ROOM_CHANGE_RATES
            
            # 💰 Tarifas - solo ver
            Permission.RATE_VIEW,
            # NO tiene RATE_CREATE_SEASON
            # NO tiene RATE_EDIT
            # NO tiene RATE_DELETE_SEASON
            
            # 📊 Reportes - solo básicos, NO financieros
            Permission.REPORT_VIEW_BASIC,
            Permission.REPORT_EXPORT,
            # NO tiene REPORT_VIEW_FINANCIAL
            # NO tiene REPORT_VIEW_PROFITABILITY
            # NO tiene REPORT_VIEW_ALL
            
            # 📝 Reservas - operaciones básicas
            Permission.BOOKING_CREATE, 
            Permission.BOOKING_EDIT,  # Solo datos básicos
            Permission.BOOKING_CANCEL,  # Sin reembolso
            Permission.BOOKING_VIEW_OWN,
            # NO tiene BOOKING_CANCEL_REFUND
            # NO tiene BOOKING_MODIFY_PRICE
            # NO tiene BOOKING_VIEW_ALL
            
            # 🧾 Facturación - solo ver y crear básicas
            Permission.INVOICE_VIEW,
            Permission.INVOICE_CREATE,
            # NO tiene INVOICE_VIEW_ALL
            # NO tiene INVOICE_VOID
            # NO tiene INVOICE_DISCOUNT
            # NO tiene INVOICE_DISCOUNT_HIGH
            # NO tiene INVOICE_REFUND
            
            # ⚙️ Configuración - ninguno
            # NO tiene CONFIG_VIEW
            # NO tiene CONFIG_EDIT
            # NO tiene BACKUP_CREATE
            # NO tiene BACKUP_RESTORE
            
            # 📈 Dashboard - solo KPIs básicos
            Permission.DASHBOARD_VIEW,
            Permission.DASHBOARD_VIEW_KPI_BASIC,  # Solo métricas operativas
            # NO tiene DASHBOARD_VIEW_KPI_ALL  # No ve financieros
        ]
    }
    
    @classmethod
    def get_user_permissions(cls, user_role: str) -> List[Permission]:
        """Obtiene lista de permisos para un rol"""
        return cls.ROLE_PERMISSIONS.get(user_role, [])
    
    @classmethod
    def has_permission(cls, user_role: str, permission: Permission) -> bool:
        """Verifica si un rol tiene un permiso específico"""
        if user_role == 'admin':  # Admin siempre tiene todos
            return True
        
        permissions = cls.get_user_permissions(user_role)
        return permission in permissions
    
    @classmethod
    def filter_by_permission(cls, user_role: str, items: List[Any], 
                            permission_func) -> List[Any]:
        """Filtra items según permiso"""
        if user_role == 'admin':
            return items
        return [item for item in items if permission_func(item)]

class PermissionChecker:
    """Helper para verificar permisos en vistas"""
    
    def __init__(self, user_role: str):
        self.user_role = user_role
    
    def can(self, permission: Permission) -> bool:
        """Verifica si puede realizar una acción"""
        return RoleManager.has_permission(self.user_role, permission)
    
    def can_any(self, permissions: List[Permission]) -> bool:
        """Verifica si tiene al menos uno de los permisos"""
        return any(self.can(p) for p in permissions)
    
    def can_all(self, permissions: List[Permission]) -> bool:
        """Verifica si tiene todos los permisos"""
        return all(self.can(p) for p in permissions)
    
    def require(self, permission: Permission) -> None:
        """Lanza excepción si no tiene permiso (para usar en controladores)"""
        if not self.can(permission):
            logger.warning(f"Acceso denegado: rol {self.user_role} no tiene permiso {permission.value}")
            raise PermissionError(f"No tienes permiso para: {permission.value}")