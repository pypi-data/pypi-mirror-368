"""
Django admin configuration for BSV Integration models
"""
from django.contrib import admin
from .models import BSVWallet, BSVTransaction


@admin.register(BSVWallet)
class BSVWalletAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'address', 'balance', 'network', 'is_primary', 'created_at']
    list_filter = ['network', 'is_primary', 'is_default', 'created_at']
    search_fields = ['name', 'address', 'user__username']
    readonly_fields = ['address', 'public_key', 'private_key', 'created_at', 'last_balance_update']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'network', 'is_primary', 'is_default')
        }),
        ('Wallet Details', {
            'fields': ('address', 'public_key', 'private_key', 'balance'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_balance_update'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make private key read-only for security"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing wallet
            readonly.extend(['user', 'network'])
        return readonly

    actions = ['update_balances']
    
    def update_balances(self, request, queryset):
        """Admin action to update wallet balances"""
        updated = 0
        for wallet in queryset:
            try:
                wallet.update_balance(force_refresh=True)
                updated += 1
            except Exception as e:
                self.message_user(request, f"Failed to update {wallet.name}: {e}", level='ERROR')
        
        if updated:
            self.message_user(request, f"Successfully updated {updated} wallet balances.")
    
    update_balances.short_description = "Update selected wallet balances"


@admin.register(BSVTransaction)
class BSVTransactionAdmin(admin.ModelAdmin):
    list_display = ['txid_short', 'wallet', 'transaction_type', 'amount', 'recipient_address', 'created_at']
    list_filter = ['transaction_type', 'created_at', 'wallet__network']
    search_fields = ['txid', 'recipient_address', 'wallet__name', 'wallet__address']
    readonly_fields = ['txid', 'created_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('wallet', 'txid', 'transaction_type', 'amount', 'fee')
        }),
        ('Recipients & Message', {
            'fields': ('recipient_address', 'op_return_message')
        }),
        ('File Information', {
            'fields': ('content_type', 'file_name', 'file_size'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def txid_short(self, obj):
        """Display shortened transaction ID"""
        return f"{obj.txid[:8]}...{obj.txid[-8:]}" if obj.txid else "-"
    txid_short.short_description = "Transaction ID"
    
    def get_readonly_fields(self, request, obj=None):
        """Make transaction details read-only after creation"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing transaction
            readonly.extend(['wallet', 'transaction_type', 'amount', 'recipient_address'])
        return readonly

    actions = ['view_on_blockchain']
    
    def view_on_blockchain(self, request, queryset):
        """Admin action to view transactions on blockchain explorer"""
        for transaction in queryset:
            network = transaction.wallet.get_network()
            base_url = "https://whatsonchain.com" if network == 'main' else "https://test.whatsonchain.com"
            url = f"{base_url}/tx/{transaction.txid}"
            self.message_user(
                request, 
                f"View transaction {transaction.txid[:8]}... at: {url}",
                level='INFO'
            )
    
    view_on_blockchain.short_description = "View selected transactions on blockchain"
