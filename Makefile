VERSION := $(shell cat version)

SRC_FILE := grub-$(VERSION).tar.xz
SIGN_FILE := $(SRC_FILE).sig

URL := https://ftp.gnu.org/gnu/grub/

URL_FILE := $(URL)$(SRC_FILE)
URL_SIGN := $(URL)$(SIGN_FILE)

get-sources: $(SRC_FILE) $(SIGN_FILE)

$(SRC_FILE):
	@wget -q -N $(URL_FILE)

$(SIGN_FILE):
	@wget -q -N $(URL_SIGN)

import-keys:
	@if [ -n "$$GNUPGHOME" ]; then rm -f "$$GNUPGHOME/linux-pvgrub2-trustedkeys.gpg"; fi
	@gpg --no-auto-check-trustdb --no-default-keyring --keyring linux-pvgrub2-trustedkeys.gpg -q --import *-key.asc

verify-sources: import-keys
	@gpgv --keyring linux-pvgrub2-trustedkeys.gpg $(SIGN_FILE) $(SRC_FILE) 2>/dev/null

.PHONY : clean
clean:
	rm -rf pkgs
