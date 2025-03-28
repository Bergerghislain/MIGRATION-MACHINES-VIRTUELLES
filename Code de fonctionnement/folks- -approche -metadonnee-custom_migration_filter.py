from nova.scheduler import filters

class MigrationCompatibilityFilter(filters.BaseHostFilter):
    """Filtre personnalisé pour vérifier la compatibilité de migration."""

    def host_passes(self, host_state, filter_properties):
        # Récupérer la valeur de l'extra-spec demandée dans le flavor
        flavor = filter_properties.get('instance_type', {})
        required_direction = flavor.get('extra_specs', {}).get('migrate_direction')
        if not required_direction:
            # S'il n'y a pas de contrainte, laisser passer
            return True

        # Récupérer les métadonnées de l'hôte (stockées via host aggregates)
        host_metadata = host_state.host_ram_free  # par exemple, utilisez l'attribut adapté
        # Généralement, Nova fusionne les métadonnées des agrégats dans un dictionnaire associé à l'hôte.
        # On suppose ici qu'une clé "migrate_direction" a été fusionnée dans l'état de l'hôte.
        host_direction = host_state.get('migrate_direction')
        
        if host_direction is None:
            # Si aucune info n'est trouvée sur l'hôte, on refuse par sécurité
            return False

        # Vérifier la compatibilité
        if host_direction == required_direction:
            return True
        return False

