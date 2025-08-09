
# Design of the Iris Global P2P system for IDS

This document describes the general design of Iris P2P System and its integration into Slips. First, we describe the features and overall goal of Iris. Next, we discuss the assumptions that we make about the environment. Furthermore, we show the general architecture of the system with all components and responsibilities. Last, we elaborate on the protocols that we have designed to achieve the aforementioned goals.

## Goals of the System
The high level goal of Iris is to allow IDS instances (Slips in particular) to communicate directly with each other without any central authority and to securely exchange threat intelligence data. Threat intelligence data might contain confidential information, and that is why peers should be able to share specific data only to a trusted subset of peers.

### Functional Requirements
- Peers shall be able to be members of trusted groups to allow message exchanges only within a subset of peers. We introduce a solution called Organisations for this problem.
- Peers shall be able to alert the network or trusted groups of peers with an alert message about an IoC. This information can be used by other IDS instances to block the malicious IoC. For that, we designed a solution called Alert Protocol.
- Peers shall be able to share threat intelligence files with the whole network or trusted groups of peers. For this we designed a File Sharing Protocol.
- Peers shall be able to ask other peers for their opinion about a given IoC (an IP address, a domain, etc.). To support this feature we designed a Network Opinion Protocol.

### Non-functional Requirements
We consider information security as the main non-functional requirement. In particular, Iris tries to address, as much as possible:
- Confidentiality - ensure that only authorised peers can access the data. 
- Integrity - ensure that the exchanged data are not altered.
- Availability - ensure that the system is available.

## Trust Model Assumption
Iris does not try to solve the issue of how to trust other peers nor how to trust the data in the network, since it is a non-trivial problem. For that reason, we designed a separated protocol, called Fides, that focuses on this particular issue for P2P networks. Both programs were designed in tight cooperation to ensure their mutual compatibility.

Therefore, we assume the existence of a black-box trust model, called Fides, that Iris queries inside each peer to retrieve a value called *service trust* . The service trust value is an estimation of how much a peer can be trusted to provide a good service. Iris uses this value in its design, for example, to favour more trusted peers when downloading a TI file. For more details about the computation of trust, see the design of Fides.

##### Definition of Service Trust
Service Trust *stp* denotes a belief about how much we trust that a given peer *p*  will provide a good service. It is a real number between 0 and 1 where a value closer to 1 represents larger trust. On the other hand, a value closer to zero stands for no trust all.

	stp ∈ [0,1]
	p ∈ {p1, ..., pn}

Fides provides Iris with the option to report misbehaviour of any peer (such as providing incorrect files, not following the defined protocol, etc.). The reporting of peers should result in decreasing their service trust. That is why Iris does not need to remember the reputation or trust of peers.
Iris does not manipulate the application data shared between peers. It treats the content as an unknown raw stream of bytes. Iris serves solely as a networking layer that is responsible for delivering the messages and the security of the system.

## Architecture Overview
In total, there exists three major components in Iris, as shown in Figure 4.1:


![image](https://github.com/stratosphereips/iris/assets/2458867/07593fef-b0d5-46ea-b0f7-85ffb3567ee7)

- Slips [19] - Slips is a modular IPS implemented in Python. The Slips instance monitors the behaviour on the local machine and in case of suspicious events might decide to ask the network for advice, share threat intelligence data or alert the network. Slips uses Redis as a database system.
- Fides Trust Model [17] - Fides is implemented as a Slips module in Python. If Slips wants to interact with the network, it asks Fides. Fides forwards the task through a Redis channel to Iris and subscribes for a reply in the Redis channel. Fides determines the credibility of the aggregated peers’ replies and returns it back to Slips.
- Iris P2P System - Our networking stack that provides direct communication with other peers. Iris is responsible for secure communication, privacy of trans- ferred data, and delivery of requests and corresponding responses. Iris is built on top of the LibP2P[29] project that provides libraries for P2P networking. Figure 4.2, shows an analysis of responsibilities between Iris and the LibP2P project.
 
## Peers Joining the Network
The mechanism for new peers to join the network is problematic. All methods that we have described either introduce more attacks vectors or convert the network into P2P hybrid or less decentralised. Even though it is possible that the best approach would be to use a mixture of methods, we only implemented bootstrapping nodes and the manual configuration of known peers and organisations.


![image](https://github.com/stratosphereips/iris/assets/2458867/9442e384-be17-48c6-afcb-987ce8f14909)

## Iris Usage of Distributed Hash Table
The Distributed Hash Table (DHT) plays an essential role in Iris. We use S/Kademlia DHT implemented with some modifications by the LibP2P project. The DHT in our system serves three purposes (the security aspect of all use cases is discussed later):

1. The DHT stores the providers of TI files. The DHT stores the providers of every shared file in the system. 
2. The DHT stores the members of Organisations. The DHT stores information about pre-trusted groups of peers. 
3. Peer routing. Peer routing is a mechanism to locate peers in the network using only their identifiers. The LibP2P project already supports this feature, so it is not implemented in Iris.
  
## Organisations as Trusted Groups
Iris introduces a new concept for P2P networks called *Organisations*. An organisation represents a trusted group of peers in the P2P network. The main incentive to create Organisation is that security practitioners on the Internet naturally form groups (companies, foundations, group of friends, etc.), where they know each other, trust each other to some degree, share common interests, and share data. It is a basic human methodology to counteract adversaries. Therefore, having cryptographically-verified groups was necessary for a secure P2P network.

There are two main motivations behind this concept:
- The use of Organisations allow Iris to exchange data only with peers within a specific trusted group. 
- Organisations provide the initial configuration of who to trust in the trust model. Note that the Fides trust model takes organisations’ memberships into consideration and uses this to compute the value of *service trust* for a given peer.

### Definition of Organisation
Internally, Iris identifies an organisation in the same way as LibP2P defines identifiers of peers, which is by using a cryptographic key-pair. An identifier of an organisation is then a *multihash* of its public key.

Apart from its simplicity, identifying an organisation like this also ensures that peers’ identifiers and organisations’ identifiers share *the same key space*, which is an important fact in organisation member discovery and secure storage.

Any peer *p* can become a member of an organisation *o* by having its ID digitally signed by the organisation’s private key. Later, when the peers introduce themselves to other peers, they present also the signature and the organisation’s ID. If the organisation matches any organisation in the receiver’s trusted list, the receiver can verify the signature and consider the given peer as a member of the given organisation.

Note that a peer does not have to be a member of an organisation *o* in order to trust peers that are members of *o*. Knowledge of the organisation’s identifier is enough to verify other members.

### Discovery of Organisations and Organisations’ Members

Iris does not provide any way to trustworthily disclose organisations identifiers to users. Also, Iris does not provide users with a way to verify that an organisation’s identifier truly belongs to the given organisation in the real world. Therefore, every organisation should choose some technique to ensure the trustworthiness of its own published ID. For example, asking a Central Authority from a Public Key Infrastructure to issue them a certificate, or use public social networks. It is then the users’ responsibility to verify the correctness of a given organisation ID before trusting it. 

After joining the network, it is in the new peer’s interest to establish a connection with at least some peers from the trusted organisation. The reason is that if the peer trusts its organisation, there is a bigger probability that these peers will not be under the control of an adversary. It is the only heuristic the new peers have because otherwise they may end up only talking to unknown peers.

Since peers would like to find other members of the organisation they trust, Iris should provide a way to achieve that. A naive approach would be to traverse the whole network as a graph using depth-first or breadth-first search until the peer finds at least a minimum number of such peers. However, with a larger network, this approach introduces unnecessary network overhead. Therefore, Iris uses the DHT to automatically discover the members of an organisation. This is done using the same mechanism the DHT has to find the *keys* of files, but instead it finds the IDs of an organisation, since the ID of an organisation shares the same key space as files IDs.

Organisations can also publish the identifiers of its peers on the Internet in any way they want. That way users can use publicly known peers in their configuration to connect directly to these trusted peers.

#### Storing Members in the DHT
Since we have defined the organisations’ IDs from the same space as peers’ IDs, we can use organisations’ IDs as keys in the DHT. As the corresponding value for the key, we store a list of peer IDs that belong to the given organisation. This makes it easier and secure to find which peers belong to which organisation.

To support this feature, we define two new methods that use the DHT:
1. *membership(o)* - using this method a peer advertises themselves as a member of organisation *o* in the DHT. To do so, the peer launches a node lookup procedure with the key *o* to find responsible peers for the key *o*. A responsible peer for a key is the peer that is closest and therefore preffered to tell others about the content of that key. After that, the peer sends to all responsible peers a claim of being a member of *o* with a digital signature. The responsible peers verify the signature and if the signature is correct, they append the peer to an already existing list of members, or they create a new one if necessary.
2. *members(o)* - using this method a peer can find advertised members of an organisation *o*. First, the peer finds all responsible peers for the *o* key. After that, it asks the responsible peers about the value of the corresponding key *o*, which contains the members.
 
For this method to work, whenever peers that are members of some organisation join the network, they shall advertise themselves as members of the organisations in the DHT using the membership method. Later, whenever any peer wants to connect to some pre-trusted peers, it can query the DHT using the members method.

### Security for Storing Organisation Members in the DHT

Since DHT plays an important role in our organisation mechanisms, we need to consider all the threats that come along with it. There are two main security risks: 
1. Attackers controlling the responsible peers for an organisation.
2. Poisoning of the DHT with fake members of an organisation.
 
#### Attacker Controlling Responsible Peers for a Given Organisation
An attacker can try to control the information in the DHT by controlling the peers that are responsible for storing a list of organisation’s members. This would have fatal consequences and could result in lost communication between organisation members because the malicious peers could return anything instead of the list with organisation’s members.

Remember that responsible peers are the ones whose IDs’ are closest to the stored key. Thus, the attacker would have to control the peers that are closest to the given key. However, it is enough for the attacker to be closer than everyone else in the network. And the list of currently closest peers in the network is fairly easy to acquire by simply launching the node lookup procedure.

The cost of this attack grows with the size of the network because if there is a large number of peers in the network, the attacker has to generate large number of peer IDs in order to find and control the closest ones. However, as has been shown in[^1], that such attack may take only some seconds to find the closest peers in the IPFS network, which already has thousands of active peers. Most probably our network will be even smaller, that is why we have to consider this attack vector very seriously.

That being said, our goal in mitigating this attack is to prevent the attacker controlling the closest peers to the DHT key. But since the DHT key is actually an organisation ID and we generate the organisation ID the same way as peer ID, we essentially own the peer that has ID with distance zero from the organisation key because d(x, x) = x ⊕ x = 0.
That is why, if we deploy a peer into the network with the same ID as the organisation ID, the attacker can never control all the closest peers. Utilising this technique, we can effectively mitigate this attack vector.

A very important advantage of sharing the key space is that if there is a peer in the network with **the exact same ID** as an organisation, we can automatically consider this peer non-adversarial and confirmed to be maintained by the organisation, and use them straight away as a responsible peer. Otherwise it implies that the attacker controls the private key of the organisation and the whole trust mechanism of the organisation is breached.

#### Poisoning the DHT with Fake Organisation Members
An attacker could try to generate a large number of sybil peers and falsely claim to be a member of any organisation to poison the list with members in the DHT. However, in order to poison the correct list of organisation members, the sybil peer needs to provide the true ID of the victim organisation (because the ID is used as a key in the DHT). And since the organisation ID is also a public key, the responsible peers can easily verify if the sybil peer owns a correct signature generated by the organisation’s private key. Sybil peers will not be able to provide such signature and thus they will not be able to poison the DHT.
The only option is that the attacker controls the responsible peers to skip the verification process. However, if the attacker controls the responsible peers, we talk about the attack we have just described in previous Subsection.

[^1]: Bernd Prünster, Alexander Marsalek, and Thomas Zefferer. “Total Eclipse of the Heart – Disrupting the InterPlanetary File System”. In: 31st USENIX Security Symposium (USENIX Security 22). Boston, MA: USENIX Association, Aug. 2022. url: https://www.usenix.org/conference/usenixsecurity22/presentation/prunster]

## Alert Protocol
The Alert Protocol is one of the contributions of Iris that provides alerting to other peers in the network about an IoC. The idea is that when Slips (or any IDS) confidently detects an IoC(such as IP address, domain, etc.) it wants to warn other peers in the network. When a peer wants to block a new attack, the expected life of the IoC is measured in days at most (and hours at least), therefore we assume that peers want to receive the alert as soon as possible. Note that the content of alerts is irrelevant for Iris.

Peers might want to share the alerts only within a trusted organisation. There are several reasons for that. One of them is that alerts contain confidential data. Another one is to prevent attackers from eavesdropping on the alerts of their victims to adapt their behaviour. For that reason, Iris allows to specify authorised organisations to receive alert messages. If an alert is addressed only to a subset of organisations, peers spread the alert only to further authorised peers along with information of who is authorised to receive the alert for further propagation.

To understand how the Alert Protocol can spread different messages better, we have conducted experiments to see if we can optimise the configuration of spreading algorithms with the *service trust values* provided by Fides.
 
## File Sharing Protocol
Another contribution of Iris is a File Sharing Protocol to share threat intelligence data. The goal is to notify peers in the network about a new available file in a reasonable time and to allow all authorised peers to download the file, therefore to design some form of a reading access control per organisations. With file we mean a list of Threat Intelligence data, because it is usually more efficient to send more than one IoC simultaneously, but it is not mandatory.

A naive approach would be to propagate the file content similarly to the alerts described [before](#alert-protocol). However, that would introduce unnecessary network overhead, because not every peer wants to download every available file for various reasons - connection bandwidth limitation, no interest, etc.

The special need is that peers do not want to distribute the content of files to everyone in the network, since peers may not want or need that threat intelligence. Because of that, first we publish  the *metadata* of the shared TI file, and then the peers that want that particular TI file can ask for it in the P2P network.

The Iris File Sharing Protocol stores the providers of files in the DHT similarly as IPFS [^4]. Storing providers in the DHT is practical because peers can easily advertise themselves as providers just by writing a value into the DHT. Also, any peer can easily query the DHT to obtain an up-to-date list of providers for the given file. However, storing the providers in the DHT is not sufficient because we need to also somehow notify peers in the network about the existence of the file in the first place.

An overall diagram of how to share a file can be seen in Figure 4.3.

![image](https://github.com/stratosphereips/iris/assets/2458867/50328194-4a7d-4350-b949-6669ad1936c0)

[^4]: Juan Benet. “IPFS - Content Addressed, Versioned, P2P File System”. (July 2014).

### Storing File Providers in the DHT
DHT stores information about the peers that share certain files, called file providers. The files themselves are not stored in the DHT, but the file hash is used as a key in the DHT. Thus, for every shared file with a hash f in the network, there shall be a list of provider peers stored in the DHT as a key-value pair *(f : l)*.

Iris implements two methods using the DHT to support this functionality:
1. *provide(f)* - A peer can claim to be a provider of a file *f* by calling this method. As a result, the responsible peers for they key *f* append this peer to the list of providers of the *f* key (or create a new one if the list does not exist). Note that responsible peers cannot verify this claim as they may not be authorised to access the file. Figure 4.4 depicts this process.
2. *providers(f)* - A method to query the DHT for a list of providers for the given key *k*. Internally it launches the node lookup procedure to find responsible peers and ask them for a corresponding value - the list of providers.

![image](https://github.com/stratosphereips/iris/assets/2458867/7a62c16d-f587-4768-87bb-8fc4c0fdeb54)

### Notification of Authorised Peers
Iris uses Epidemic Protocols (similarly as for Alerts) to spread metadata of files to notify peers about their existence. An example can be seen in Figure 4.5a. The metadata contains a description of the file and the hash of the file that recipients can use to query the DHT to find a list of providers of the file. This way, every peer can decide based on the received metadata file whether it wants to download the file or not.

![image](https://github.com/stratosphereips/iris/assets/2458867/ec330d74-ca28-4b08-9ac6-32b32f946161)

Spreading algorithms depend on how the set of peers that receive a message is chosen. In the case of metadata files, should the metadata be shared with the whole network? We conclude that not. The reason is that by disclosing the threat intelligence metadata to unauthorised peers, we might face a side channel attack. A smart attacker could monitor the messages originating from its victims to learn about their defence mechanisms and adapt to their behaviour.

For this reason, Iris adds a list of authorised organisations into the metadata message, and peers must only forward the metadata to members of authorised organisations. In other words, if only organisation *O* is authorised to download a file, then only the members of the organisation *O* should receive the metadata message. A diagram of sharing metadata only to authorised peers can be seen in Figure 4.5b. This requires every peer to have always at-least one open connection with members from their organisations.

However, not all files share the same importance. For example, all authorised peers should promptly find out about a new file with high-risk threat intelligence, even at the cost of flooding the network with messages. On the other hand, less important threat intelligence files can take longer to spread without any cost. Therefore, we propose **two severity levels** of shared files. By setting the appropriate severity level, the network should guarantee to spread the metadata message to all authorised peers in a different way:

- CRITICAL - by setting a file to severity CRITICAL, the network should guarantee to spread file metadata to all authorised peers as fast as possible.
- NORMAL - by setting a file to severity NORMAL, the network should also guarantee to spread the file metadata to all authorised peers but try to minimise flooding of the network with messages.

Separating threat intelligence files into two severity levels may be useful for using different spreading algorithms and thus optimise the use of network’s resources. We conducted an experiment to answer this question.

### Reading Access Control
Even though we share metadata of files only to authorised peers, it does not prevent unauthorised peers from knowing the IDs of the shared files. For example, we cannot guarantee that the responsible peers that store provider records in the DHT are authorised to access the given file. Most probably the responsible peers will be unauthorised to access the file. And we cannot prevent responsible peers from disclosing the file hash. After the possible disclosure of a file hash, anyone can query the providers in the DHT and try to download the file from them.

Thus, providers themselves have to verify that every peer that wants to download a file has authorisation to do so. Every peer can ask to be authorised by providing the organisation’s signature. The provider peer verifies the signature and eventually decides to sends the file or not.
In the case that the shared file has no access control restrictions, providers do not demand any form of authorisation. Also, metadata of this file can be spread to all peers in the network.

### Downloading Files
To download a file, peers query the DHT to get a list of providers for the given file. Peers then choose a provider from the list and try to download the file. If the file has access-control restrictions, peers also present their organisation signatures that authorise them to access the file. If the provider provides an incorrect file, the peer needs to try another provider from the list. The diagram of this process can be seen in Figure 4.6.

![image](https://github.com/stratosphereips/iris/assets/2458867/39a601f2-8e4f-4a4d-98bf-844871796de5)

After downloading a file, peers can decide whether they want to be listed in the DHT as another provider of the file. By advertising themselves as new providers, they help an original provider because suddenly more peers allow to download the file from them.

### Security of the File Sharing Protocol
There are two major security risks related to the use of DHT for file sharing: an attacker controlling the responsible peers for a file, and poisoning the DHT with fake providers of the file.

#### Attacker Controlling Responsible Peers for Given File
An attacker can try to control the information in the DHT by controlling the responsible peers. As a consequence, this would lead to a disruption of a service because peers would not be able to query the providers - thus to download the file. Remember that, to control the responsible peers, the attacker needs to own peers that are the closest to the given key in the DHT key space. The cost of this attack grows with the number of peers in the network. But as shown in [^1], even in the original IPFS network [^2] an attacker can target one DHT key in a matter of minutes.

However, this attack assumes that the attacker knows about the file hash, otherwise it cannot attack the hash key in the DHT. On the other hand, we cannot prevent the attacker from discovering the file hash as the file hash is not secret information.

This attack can be mitigated a little bit by splitting files into smaller chunks. Nonetheless, our code does not implement chunking and thus is vulnerable to this attack vector.

#### Poisoning the DHT with Fake File Providers
An attacker might generate many fake peers that all claim to be providers of a certain file. And as shown in [^1], the generation of fake peers in the IPFS P2P network is extremely easy. Peers responsible for storing the list of providers in the DHT may not be able to verify these claims as they may not be authorised to read the file and verify the hash.

As a result of this attack, when a victim peer asks for a list of providers of a specific file, it receives a list of peers, but the majority of them may be fake. The victim then needs to spend a non-trivial amount of time filtering out the fake peers by trying to download the file. A fake file can be recognised by verifying that the hash of the given file does not equal to the ID of the file. However, peers have to download the whole fake file first in order to detect that the content is wrong. This essentially results in a DoS attack. A diagram of this attack can be seen in Figure 4.7.

![image](https://github.com/stratosphereips/iris/assets/2458867/17726e50-54f6-411f-86c8-56c667a6f606)

In our environment, Iris relies on *service trust value* provided by Fides trust model for choosing specific providers from the list of all providers to download the file. If these providers give us incorrect files, Iris reports them to Fides, and future interactions with them will be less trusted. If Fides works correctly, in the long run, the legitimate providers should possess a bigger service trust and thus we should be able to promptly find the correct providers.

## Network Opinion Protocol
Iris implements a protocol to allow peers to ask other peers about their opinions on a specific IoC. The idea is that the Slips instance encounters a suspicious resource (e.g. an IP address, a domain, etc.) and needs to asks other peers for an opinion.

### Design of Network Opinion Protocol
This protocol was designed so that a peer always asks more peers than just the ones it is connected to. However, a peer cannot ask the whole network. A peer doesn’t know the size of the network and the number of responses could be enormous. In the worst-case scenario, a peer could even launch a DDOS attack against itself.

That is why this protocol was designed in a way that spreads the request message in an epidemic style but contains the outbreak by automatically terminating it after some time. The termination is implemented in the Network Opinion Protocol messages by a special field called *time to live (TTL) value*. The peer that asks for an opinion, sets the initial TTL value of the request and sends the request to a set of peers. Every peer that receives the request, decrements the TTL value by one and forwards the request to other peers. This propagation is done recursively until the TTL reaches zero. When the TTL reaches zero, the current peer stops further propagation.

Every peer that received the request (no matter if the peer propagated the request further to other peers or not) also forwards the request to a local Slips instance to acquire a local opinion. The peer signs the local opinion with its private key and encrypts the local opinion using the original requester’s public key. This is very important for the overall confidentiality of the Iris P2P network. No message can be opened by any intermediary peer that is not the originator of the request.

After that, peers collect together the local encrypted opinions and opinions from responses of other peers. The accumulated opinions are returned as a response to the sender. This way, no peers can see the contents of opinions of other peers because every opinion is encrypted using the original requester’s public key.

Lastly, every peer that receives the request should make sure that it has not already processed the request before. If yes, the peer should not process the request again. Otherwise, peers could do the same work multiple times because they might be asked multiple times by different peers.
An overview of just just-described process that propagates the opinion request can be seen in Algorithm 1 and in Figure 4.8.

![image](https://github.com/stratosphereips/iris/assets/2458867/8dcf9b64-1510-41fa-b330-450740755e63)

![image](https://github.com/stratosphereips/iris/assets/2458867/7cf7544f-5117-4ff0-989c-63d17a7d2053)

Nonetheless, two questions regarding the forwarding of opinion requests arise:

1. How many opinions does a peer want to acquire about a potential malicious IoC? For a rigorous answer, we should find a heuristic that would provide us an approximation to the probability of two random peers dealing with a similar attack. Using this heuristic, we could decide how many opinions a peer needs in order for some of the opinions to be useful. However, the answer for this question is out of scope of this thesis and left for future work. For our current work, we approximate that an ideal number of total received opinions is around 100.

	In Iris, using the previously described process of opinion request propagation, the total number of recipients is calculated as the number of nodes in the spreading tree minus one (the original requester) - see Equation 4.2.
	
  ![image](https://github.com/stratosphereips/iris/assets/2458867/8a0271a1-4939-4108-8000-e195ed038d60)
	
	For our implementation, we use a strategy that forwards a request to 3 peers with an initial value of TTL=4. This results in a total number of recipients being up to 120 (P4i=0 = 3i − 1 = 120).

2. How should peers choose which other peers are the recipients of the opinion request? One approach is to choose recipients completely randomly. Another approach is to use *service trust value* from Fides as a heuristic when sampling recipients from the list of candidates. Since service trust is defined exactly as the belief that peers would provide a good service, it is a rational value to use for choosing recipients.

	It is also important for peers not to ask every time the same peers about an opinion. We would like to allow a bit of variability that would slightly favour the more trusted peers. That is why Iris chooses recipients from candidates with a probability that is exponentially weighted with the candidates’ service trust. Iris does this by firstly transforming service trust values of all candidates using exponential function $f(st) = \frac{a^{st}−1}{a-1}$ with a constant value a = 10 (see the function plotted in Figure 4.9). After that, Iris normalises the transformed values, which represent the probabilities of the candidates being chosen.

![image](https://github.com/stratosphereips/iris/assets/2458867/69c642e5-be84-4ac7-802b-af77d55f7b3f)

### Security of the Network Opinion Protocol
Encrypting and signing the messages provides confidentiality and integrity of the opinions. Every peer knows who the original requester was and cannot tamper with the forwarding request. Also, no intermediate peer can see into the opinions that are not addressed to him. This allows peers to respond with confidential data because nobody except the original requester can see the data. Also, every opinion is digitally signed by opinion’s author and that is why the original requester knows who provided the opinions.

The only potential attacks done by adversarial peers using this protocol are based on lying to mislead the peer that requested the information. However, this is not an issue for Iris, but for the Fides trust model, and it is addressed in that work.
