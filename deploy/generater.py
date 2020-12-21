import os
import sys
import yaml
import pdb

CURRENT_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(CURRENT_PATH, "../config.yaml")
TEMPLATE_PATH = os.path.join(CURRENT_PATH, "template.yaml")


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
    if phase == "gray":
        rancher_project_id = "c-r89km:p-ltprd"
        namespace = config["project_name"] + "-gray"
        OUTPUT_PATH = os.path.join(CURRENT_PATH, "deploy-gray.yaml")
    elif phase == "production":
        rancher_project_id = "c-r89km:p-4l7tn"
        namespace = config["project_name"]
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
    if phase == "gray":
        cgi_deployment["spec"]["replicas"] = 1
    else:
        cgi_deployment["spec"]["replicas"] = int(config["replicas"])
    cgi_deployment["spec"]["selector"]["matchLabels"]["app"] = project_cgi_name
    cgi_deployment["spec"]["template"]["metadata"]["labels"]["app"] = project_cgi_name

    container = cgi_deployment["spec"]["template"]["spec"]["containers"][0]
    container["name"] = project_cgi_name
    # container["image"] = "harbor.bigo.sg/bigo_ai/icpm/content/cgi/" + str(config["project_name"]) + ":latest"
    container["command"][5] = str(config["workers_per_replica"])
    container["livenessProbe"]["httpGet"]["path"] = config["inference_prefix"] + "/ping"
    
    # add environments
    cgi_env = []
    for item in config["environments"]:
        cgi_env.append(item)
    if config["use_redis"]:
        redis_env = {
            "name": "REDIS_SERVER_HOST",
            "value": "redis-server.common"}
        cgi_env.append(redis_env)
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
    for model in config["models"]:
        ### config model deployment ###
        deployment = model_deployment_template.copy()
        deployment["metadata"]["name"] = model["name"]
        deployment["metadata"]["namespace"] = namespace
        if phase == "gray":
            deployment["spec"]["replicas"] = 1
        else:
            deployment["spec"]["replicas"] = int(model["replicas"])
        deployment["spec"]["selector"]["matchLabels"]["app"] = model["name"]
        deployment["spec"]["template"]["metadata"]["labels"]["app"] = model["name"]
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
    
    ### config Ingress
    ingress = next(template)
    if phase == "gray":
        host_gray = "intelligent-content-gray.bigoml.cc"
        ingress["metadata"]["name"] = host_gray + "-" + project_cgi_name
        ingress["spec"]["rules"][0]["host"] = host_gray
    else:
        ingress["metadata"]["name"] = "evg-ml.bigo.sg-" + project_cgi_name
    ingress["metadata"]["namespace"] = namespace
    if "inference_prefix" in config and config["inference_prefix"] is not None:
        if config["inference_prefix"][0] == "/":
            prefix = config["inference_prefix"]
        else:
            prefix = "/" + config["inference_prefix"]
    else:
        prefix = "/"
    ingress["spec"]["rules"][0]["http"]["paths"][0]["path"] = prefix
    ingress["spec"]["rules"][0]["http"]["paths"][0]["backend"]["serviceName"] = project_cgi_name

    # dump config
    with open(OUTPUT_PATH, "a") as fw:
        fw.write(dividing)
        yaml.safe_dump(ingress, fw)

    reader.close()
    print("Generate 'deploy-{}.yaml' succeed!".format(phase))

if __name__ == "__main__":
    try:
        generate("gray")
        generate("production")
    except Exception:
        print("Generate 'deploy-gray/production.yaml' failed!\n" \
                "Please make sure 'config.yaml' has been configured correctly" \
                "and 'deploy/template.yaml' has not been changed!")
        import traceback
        traceback.print_exc()

