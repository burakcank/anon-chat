deploy:
	@echo "Backing up .env to .env.bak"
	@cp .env .env.bak
	@echo "Overwriting .env with .env.prod"
	@cp .env.prod .env || (echo "Error: Could not copy .env.prod"; cp .env.bak .env; exit 1)
	@echo "Deploying to Fly.io"
	@flyctl deploy || (echo "Error: Deployment failed, restoring .env"; cp .env.bak .env; exit 1)
	@echo "Deployment successful, restoring .env"
	@cp .env.bak .env || (echo "Error: Could not restore .env"; exit 1)
	@echo "Deleting backup .env.bak"
	@rm .env.bak
	@echo "Deployment successful"
