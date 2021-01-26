# > CONSTANTS
PATTERN_BEGIN=»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»
PATTERN_END=«««««««««««««««««««««««««««««««««««««««««««««

BUILDPACK_BUILDER=heroku/buildpacks:18
BUILDPACK_PIP_DEFAULT_TIMEOUT=2000

SIMULATOR_NETWORK_NAME=net_energysim

MODEL_NAME=charging_period_peak

MODEL_PACK_NAME=pack_energysim_model_charging_period_peak
MODEL_CONTAINER_NAME=cont_energysim_model_charging_period_peak
MODEL_BACKDOOR=3000
MODEL_PORTS=8001:8000

RABBIT_CONTAINER_NAME=cont_energysim_rabbitmq
RABBIT_USER=guest
RABBIT_PASSWORD=guest
RABBIT_PORT=5672
RABBIT_MANAGEMENT_PORT=15672
# < CONSTANTS

main: run-docker-model

# > MODEL1
run-docker-model: stop-docker-model build-docker-model start-docker-model

build-docker-model:
	@echo '$(PATTERN_BEGIN) BUILDING `$(MODEL_NAME)` PACK...'

	@pipreqs --savepath requirements.txt.tmp
	@if cmp -s "requirements.txt.tmp" "requirements.txt"; then rm requirements.txt.tmp; \
	else mv requirements.txt.tmp requirements.txt; fi

	@pack build $(MODEL_PACK_NAME) \
	--builder $(BUILDPACK_BUILDER) \
	--env PIP_DEFAULT_TIMEOUT=$(BUILDPACK_PIP_DEFAULT_TIMEOUT)

	@echo '$(PATTERN_END) `$(MODEL_NAME)` PACK BUILT!'

start-docker-model:
	@echo '$(PATTERN_BEGIN) STARTING `$(MODEL_NAME)` PACK...'

	@docker run -d \
	--name $(MODEL_CONTAINER_NAME) \
	--network $(SIMULATOR_NETWORK_NAME) \
	-e RABBIT_USER=$(RABBIT_USER) \
	-e RABBIT_PASSWORD=$(RABBIT_PASSWORD) \
	-e RABBIT_HOST=$(RABBIT_CONTAINER_NAME) \
	-e RABBIT_MANAGEMENT_PORT=$(RABBIT_MANAGEMENT_PORT) \
	-e RABBIT_PORT=$(RABBIT_PORT) \
	-p $(MODEL_PORTS) \
	$(MODEL_PACK_NAME)
	
	@echo '$(PATTERN_END) `$(MODEL_NAME)` PACK STARTED!'

stop-docker-model:
	@echo '$(PATTERN_BEGIN) STOPPING `$(MODEL_NAME)` PACK...'

	@( docker stop $(MODEL_CONTAINER_NAME) && docker rm $(MODEL_CONTAINER_NAME) ) || true

	@echo '$(PATTERN_END) `$(MODEL_NAME)` PACK STOPPED!'	
# < GATEWAY

# > NAMEKO
run-nameko-model: prep-nameko-model start-nameko-model

prep-nameko-model:
	@until nc -z $(RABBIT_CONTAINER_NAME) $(RABBIT_PORT); do \
	echo "$$(date) - waiting for rabbitmq..."; \
	sleep 2; \
	done

start-nameko-model:
	@nameko run model.service \
	--config nameko-config.yml  \
	--backdoor $(MODEL_BACKDOOR)
# < NAMEKO