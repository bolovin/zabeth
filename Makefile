
.PHONY: generate-photos
generate-md:
	poetry run python generate_photos.py

.PHONY: generate-slideshow
generate-slideshow:
	poetry run python generate_slideshow.py

.PHONY: build
build: clean generate-md generate-slideshow
	poetry run jupyter-book build --path-output out src/zabeth --verbose

.PHONY: clean
clean:
	rm -rf out
	mkdir -p out
DOCS_WORKTREE := out/docs

.PHONY: deploy
deploy: build
	git worktree prune
	git branch -f docs origin/docs
	git worktree add -f $(DOCS_WORKTREE) docs
	rsync -a --delete --exclude .git --exclude .gitattributes out/_build/html/ $(DOCS_WORKTREE)/
	printf '* !text !filter !merge !diff\n' > $(DOCS_WORKTREE)/.gitattributes
	touch $(DOCS_WORKTREE)/.nojekyll
	cd $(DOCS_WORKTREE) && git add -A && (git diff --cached --quiet || git commit -q -m "deploy site") && git push origin docs
	git worktree remove --force $(DOCS_WORKTREE)
