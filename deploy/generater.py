import os
import sys
import yaml
import time
import pdb
import copy

CURRENT_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(CURRENT_PATH, "../config.yaml")
TEMPLATE_PATH = os.path.join(CURRENT_PATH, "template.yaml")
MODELS_TAG_INFO_SAVE_PATH = os.path.join(CURRENT_PATH, "models_tag_info.txt")
FORMAT_DATETIME = time.strftime("%Y%m%d%H%M%S", time.localtime())

def retag_model_docker_image(models):
    retaged_models = []
    with open(MODELS_TAG_INFO_SAVE_PATH, "w") as fw:
        for model in models:
            docker_image = model['docker_image']
            new_docker_image = docker_image.split(":")[0] + ":" + FORMAT_DATETIME
            fw.write(docker_image + " " + new_docker_image + "\n")
            new_model = copy.deepcopy(model)
            new_model['docker_image'] = new_docker_image
            retaged_models.append(new_model)
    
    return retaged_models

def generate(phase):
    config = None
    template = None
    dividing = "---\n"

    # load config
    with open(CONFIG_PATH, 'r') as fr:
        config = yaml.safe_load(fr)
    if config is None:
        print('Could not load config in {}'.format(CONFIG_PATH))
        return
    
    # load template
    reader = open(TEMPLATE_PATH, "r")
    template = yaml.safe_load_all(reader)
    if template is None:
        print("Could not load template in {}".format(TEMPLATE_PATH))
        reader.close()
        return
    
    ### config namespace ###
    config_namespace = next(template)
    # check phase
    if phase == "grey":
        rancher_project_id = "c-f8rw4:p-rx8wc"
        namespace = "grey-content-" + config["project_name"]
        OUTPUT_PATH = os.path.join(CURRENT_PATH, "deploy-grey.yaml")
    elif phase == "production":
        rancher_project_id = "c-f8rw4:p-7s2gb"
        namespace = "content-" + config["project_name"]
        OUTPUT_PATH = os.path.join(CURRENT_PATH, "deploy-production.yaml")
    else:
        print("Phase error:{}".format(phase))
        return
    # config 
    config_namespace["metadata"]["name"] = namespace
    config_namespace["metadata"]["labels"]["app"] = namespace
    config_namespace["metadata"]["annotations"]["field.cattle.io/projectId"] = rancher_project_id

    # dump config
    with open(OUTPUT_PATH, 'w') as fw:
        yaml.safe_dump(config_namespace, fw)
    
    ### config cgi deployment ###
    cgi_deployment = next(template)
    project_cgi_name = str(config["project_name"]) + "-cgi"
    cgi_deployment["metadata"]["name"] = project_cgi_name
    cgi_deployment["metadata"]["namespace"] = namespace
    if phase == "grey":
        cgi_deployment["spec"]["replicas"] = 1
    else:
        cgi_deployment["spec"]["replicas"] = int(config["replicas"])
    cgi_deployment["spec"]["selector"]["matchLabels"]["app"] = project_cgi_name
    cgi_deployment["spec"]["template"]["metadata"]["labels"]["app"] = project_cgi_name
    if "use_labels" in config:
        cgi_node_labels_default = cgi_deployment["spec"]["template"]["spec"]["affinity"]["nodeAffinity"]\
            ["requiredDuringSchedulingIgnoredDuringExecution"]["nodeSelectorTerms"][0]["matchExpressions"][0]
        cgi_node_labels = []
        for label in config["use_labels"]:
            node_label = copy.deepcopy(cgi_node_labels_default)
            node_label["key"] = str(label["key"])
            node_label["values"][0] = str(label["value"]).lower()
            cgi_node_labels.append(node_label)
        cgi_deployment["spec"]["template"]["spec"]["affinity"]["nodeAffinity"]\
            ["requiredDuringSchedulingIgnoredDuringExecution"]["nodeSelectorTerms"][0]["matchExpressions"] = cgi_node_labels
    container = cgi_deployment["spec"]["template"]["spec"]["containers"][0]
    container["name"] = project_cgi_name
    # container["image"] = "harbor.bigo.sg/bigo_ai/icpm/content/cgi/" + str(config["project_name"]) + ":latest"
    if phase == "grey":
        container["resources"]["limits"]["cpu"] = "1"
        container["command"][7] = "4"
    else:
        container["resources"]["limits"]["cpu"] = str(config["cpu"])
    container["resources"]["limits"]["memory"] = str(config["memory"]) + "Gi"
    # container["command"][5] = str(config["workers_per_replica"])
    # container["livenessProbe"]["httpGet"]["path"] = config["inference_prefix"] + "/ping"
    
    # add environments
    cgi_env = []
    for item in config["environments"]:
        cgi_env.append(item)
    container["env"] = cgi_env
    
    # dump config
    with open(OUTPUT_PATH, 'a') as fw:
        fw.write(dividing)
        yaml.safe_dump(cgi_deployment, fw)
    
    ### config cgi service ###
    cgi_service = next(template)
    cgi_service["metadata"]["name"] = project_cgi_name
    cgi_service["metadata"]["namespace"] = namespace
    cgi_service["spec"]["selector"]["app"] = project_cgi_name
    cgi_service["spec"]["ports"][0]["name"] = "http-" + project_cgi_name
    with open(OUTPUT_PATH, 'a') as fw:
        fw.write(dividing)
        yaml.safe_dump(cgi_service, fw)
    
    ### config models ###
    model_deployment_template = next(template)
    model_service_template = next(template)
    models_info = retag_model_docker_image(config["models"])
    for model in models_info:
        ### config model deployment ###
        deployment = model_deployment_template.copy()
        deployment["metadata"]["name"] = model["name"]
        deployment["metadata"]["namespace"] = namespace
        if phase == "grey":
            deployment["spec"]["replicas"] = 1
        else:
            deployment["spec"]["replicas"] = int(model["replicas"])
        deployment["spec"]["selector"]["matchLabels"]["app"] = model["name"]
        deployment["spec"]["template"]["metadata"]["labels"]["app"] = model["name"]
        if "use_labels" in config:
            node_labels_default = deployment["spec"]["template"]["spec"]["affinity"]["nodeAffinity"]\
                ["requiredDuringSchedulingIgnoredDuringExecution"]["nodeSelectorTerms"][0]["matchExpressions"][0]
            node_labels = []
            for label in config["use_labels"]:
                node_label = copy.deepcopy(node_labels_default)
                node_label["key"] = str(label["key"])
                node_label["values"][0] = str(label["value"]).lower()
                node_labels.append(node_label)
            deployment["spec"]["template"]["spec"]["affinity"]["nodeAffinity"]\
                ["requiredDuringSchedulingIgnoredDuringExecution"]["nodeSelectorTerms"][0]["matchExpressions"] = node_labels
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        container["name"] = model["name"]
        container["image"] = model["docker_image"]
        container["ports"][0]["containerPort"] = model["port"]

        ### config model service ###
        service = model_service_template.copy()
        service["metadata"]["name"] = model["name"]
        service["metadata"]["namespace"] = namespace
        service["spec"]["selector"]["app"] = model["name"]
        service["spec"]["ports"][0]["port"] = model["port"]
        service["spec"]["ports"][0]["targetPort"] = model["port"]
        # TODO, ugly
        if model["port"] == 8500 or model["port"] == 8001:
            protocol = "grpc"
        elif model["port"] == 8080 or model["port"] == 8501 or model["port"] == 8000:
            protocol = "http"
        else:
            protocol = "http"
        service["spec"]["ports"][0]["name"] = protocol + "-" + model["name"]

        # dump config
        with open(OUTPUT_PATH, 'a') as fw:
            fw.write(dividing)
            yaml.safe_dump(deployment, fw)
            fw.write(dividing)
            yaml.safe_dump(service, fw)
    
    ### config gateway
    gw = next(template)
    gw["metadata"]["namespace"] = namespace

    # dump config
    with open(OUTPUT_PATH, "a") as fw:
        fw.write(dividing)
        yaml.safe_dump(gw, fw)

    ### config virtual service ###
    vs = next(template)
    vs["metadata"]["name"] = config["project_name"]
    vs["metadata"]["namespace"] = namespace
    vs_http = vs["spec"]["http"][0]
    if phase == "grey":
        vs_http["match"][0]["uri"]["prefix"] = "/api/grey/content/" + config["project_name"]
    else:
        vs_http["match"][0]["uri"]["prefix"] = "/api/content/" + config["project_name"]
    vs_http["rewrite"]["uri"] = "/api/content/" + config["project_name"]
    vs_http["route"][0]["destination"]["host"] = project_cgi_name

    # dump config
    with open(OUTPUT_PATH, "a") as fw:
        fw.write(dividing)
        yaml.safe_dump(vs, fw)
    
    ### config destination rule ###
    dr = next(template)
    dr["metadata"]["name"] = config["project_name"]
    dr["metadata"]["namespace"] = namespace
    dr["spec"]["host"] = project_cgi_name

    # dump config
    with open(OUTPUT_PATH, "a") as fw:
        fw.write(dividing)
        yaml.safe_dump(dr, fw)

    reader.close()
    print("Generate 'deploy-{}.yaml' succeed!".format(phase))

if __name__ == "__main__":
    try:
        generate("grey")
        generate("production")
    except Exception:
        print("Generate 'deploy-grey/production.yaml' failed!\n" \
                "Please make sure 'config.yaml' has been configured correctly" \
                "and 'deploy/template.yaml' has not been changed!")
        import traceback
        traceback.print_exc()

