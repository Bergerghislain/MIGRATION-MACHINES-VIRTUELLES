from nova.scheduler import filters

class XenCompatibilityFilter(filters.BaseHostFilter):
    def host_passes(self, host_state, filter_properties):
        src_cluster = filter_properties['request_spec']['source_cluster']
        dest_cluster = host_state.host.cluster
        # Appel externe au script JSON/jq
        return subprocess.check_output(
            f"/chemin/check_migration.sh {src_cluster} {dest_cluster}", 
            shell=True
        ).decode().startswith("OK")
