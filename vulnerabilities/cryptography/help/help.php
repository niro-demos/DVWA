<style>
	pre {
		overflow-x: auto;
		white-space: pre-wrap;
		word-wrap: break-word;
	}
</style>

<div class="body_padded">
	<h1>Help - Cryptographic Problems</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>About</h3>
		<p>
		Cryptography is key area of security and is used to keep secrets secret. When implemented badly these secrets can be leaked or the crypto manipulated to bypass protections.
		</p>
		<p>
		This module will look at three weaknesses, using encoding instead of encryption, using algorithms with known weaknesses, and padding oracle attacks.
		</p>

		<br /><hr /><br />

		<h3>Objective</h3>
		<p>Each level has its own objective but the general idea is to exploit weak cryptographic implementations.</p>

		<br /><hr /><br />

		<h3>Low Level</h3>
		<p>The thing to notice is the mention of encoding rather than encryption, that should give you a hint about the vulnerability here.</p>
		<p>
		<button id="low_button" onclick="show_answer('low')">Show Answer</button>
		</p>
		<div id="low_answer">
		<p>Password-bearing messages must not be exposed through a general-purpose decoder. Passwords are stored as one-way hashes and verified without recovering their plaintext.</p>
		</div>

		<h3>Medium Level</h3>
		<p>The tokens use authenticated encryption. Each token has a fresh nonce and an authentication tag so changes are detected before identity claims are trusted.</p>
		<p>
		<button id="medium_button" onclick="show_answer('medium')">Show Answer</button>
		</p>
		<div id="medium_answer">
		<p>AES-GCM authenticates the ciphertext, nonce, and tag together. Reusing blocks from other tokens or changing any byte causes verification to fail.</p>
		</div>

		<h3>High Level</h3>
		<p>The system uses AES-256-GCM with a fresh nonce, so modified tokens fail authentication.</p>

		<p>
		<button id="high_button" onclick="show_answer('high')">Show Answer</button>
		</p>

		<div id="high_answer">
		<p>Rather than try to explain this here, go read this excellent write up on the attack by Eli Sohl.</p>
		<p><a target="_blank" href="https://www.nccgroup.com/uk/research-blog/cryptopals-exploiting-cbc-padding-oracles/">Cryptopals: Exploiting CBC Padding Oracles</a></p>
		<p>
		If you want to play with this some more, there is a script called <a href="cryptography/source/download_oracle_attack.php" download>oracle_attack.php</a> in the sources directory which runs through the full attack with debug. You can run this either against the DVWA site or it will run locally against its own pretend web server.
		</p>
		</div>

		<h3>Impossible Level</h3>
		<p>You can never say impossible in crypto as something that would take years today could take minutes in the future when a new attack is found or when processing power takes a giant leam forward.</p>
		<p>
		The current recommended alternative to AES-CBC is AES-GCM and so the system uses that here. 256 bit blocks rather than 128 bit blocks are used, and a unique IV used for every message. This may be secure today but who knows what tomorrow brings?
		</p>
	</div></td>
	</tr>
	</table>

	</div>
	
</div>
