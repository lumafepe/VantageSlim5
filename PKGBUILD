# Maintainer: Luís Pereira <lumafepe@gmail.com>
pkgname=vantageslim5
pkgver=1.0.0
pkgrel=1
pkgdesc="Tray application for managing Lenovo vantage settings for the Legion Slim5 14APH8"
arch=('any')
url="https://github.com/lumafepe/VantageSlim5"
license=('MIT')
depends=('python' 'python-pyqt5' 'polkit')
makedepends=('python-setuptools')
source=("lenovo_tray.py"
        "requirements.txt")
sha256sums=('dbf4b7187f276677cbc7a8c159bc1113ece15ee07223f3afdf4fb64a330886f645aebc97885656d0a7f25fcc8bdf45bdf32ca0aa68cad31452d786c34496d67a'
            'bf6cc2669e5922c1c4553b6d6e557cfc8eeb0bba54ec964c8def3fa4ecdcdbcdcae20f1a7eda83bdbbf2b25b905c37621ae01d227a04f8715c1ab2fd4b6f116d')

prepare() {
	:
}

build() {
	:
}

check() {
	:
}

package() {
	# Install the Python script
	install -Dm755 "$srcdir/lenovo_tray.py" "$pkgdir/usr/bin/vantageslim5"
	
	# Install requirements as documentation
	install -Dm644 "$srcdir/requirements.txt" "$pkgdir/usr/share/doc/$pkgname/requirements.txt"
}
