class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/99/37/d3b299b6125272d9e11cf675281baed8e27632e93175ed9784862db65e95/trmd-0.1.15.tar.gz"
  sha256 "15a931640d807011f5b7c489169cdb53998639fbb4949ebe46fb948e28a80404"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
