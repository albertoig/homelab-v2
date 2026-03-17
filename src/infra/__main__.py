"""
Pulumi program to deploy MetalLB to Kubernetes cluster.

Usage:
    poetry run pulumi up
    poetry run pulumi preview
    poetry run pulumi destroy
"""

import pulumi
import pulumi_kubernetes as k8s
import pulumi_kubernetes.apiextensions as apiextensions
import pulumi_kubernetes.helm.v3 as helm

# Get configuration
config = pulumi.Config()
environment = config.get("environment") or "local"
kubeconfig_path = config.get("kubeconfig") or "~/.kube/config"
metallb_ip_range = config.require("metallb_ip_range")
metallb_namespace = config.get("metallb_namespace") or "metallb-system"
metallb_chart_version = config.get("metallb_chart_version") or "4.0.0"


# Create Kubernetes provider
k8s_provider = k8s.Provider(
    "kubernetes",
    kubeconfig=kubeconfig_path,
    opts=pulumi.ResourceOptions(
        delete_before_replace=True,
    ),
)


# Deploy MetalLB Helm chart
metallb_chart = helm.Chart(
    "metallb",
    helm.ChartOpts(
        chart="metallb",
        version=metallb_chart_version,
        namespace=metallb_namespace,
        fetch_opts=helm.FetchOpts(
            repo="https://metallb.github.io/metallb",
        ),
        values={
            "controller": {
                "tolerations": [
                    {
                        "effect": "NoSchedule",
                        "operator": "Exists",
                    }
                ],
            },
            "speaker": {
                "tolerations": [
                    {
                        "effect": "NoSchedule",
                        "operator": "Exists",
                    }
                ],
            },
        },
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
    ),
)


# Create IP Address Pool for MetalLB
ip_address_pool = apiextensions.CustomResource(
    "default-address-pool",
    api_version="metallb.io/v1beta1",
    kind="IPAddressPool",
    metadata={
        "name": "default-pool",
        "namespace": metallb_namespace,
    },
    spec={
        "addresses": [metallb_ip_range],
        "autoAssign": True,
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[metallb_chart],
    ),
)


# Create L2 Advertisement (required for MetalLB to work)
l2_advertisement = apiextensions.CustomResource(
    "l2-advertisement",
    api_version="metallb.io/v1beta1",
    kind="L2Advertisement",
    metadata={
        "name": "l2-advertisement",
        "namespace": metallb_namespace,
    },
    spec={
        "ipAddressPools": ["default-pool"],
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[ip_address_pool],
    ),
)


# Export deployment information
pulumi.export("environment", environment)
pulumi.export("metallb_namespace", metallb_namespace)
pulumi.export("metallb_ip_range", metallb_ip_range)
pulumi.export("ip_pool_name", ip_address_pool.metadata["name"])
pulumi.export("l2_advertisement_name", l2_advertisement.metadata["name"])
