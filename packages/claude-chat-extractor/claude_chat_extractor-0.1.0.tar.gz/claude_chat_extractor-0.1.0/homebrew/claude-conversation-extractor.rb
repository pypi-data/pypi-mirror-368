class ClaudeConversationExtractor < Formula
  desc "Extract Claude conversations to markdown format efficiently"
  homepage "https://github.com/yourusername/claude-conversation-extractor"
  url "https://files.pythonhosted.org/packages/source/c/claude-conversation-extractor/claude-conversation-extractor-0.1.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"
  license "MIT"
  head "https://github.com/yourusername/claude-conversation-extractor.git", branch: "main"

  depends_on "python@3.12"

  def install
    system "python3", "-m", "pip", "install", *std_pip_args, "."
  end

  test do
    system "#{bin}/cce", "--help"
  end
end
