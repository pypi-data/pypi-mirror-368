# Test and experiments to verify the clients, servers and methodology of Iris

The experiments to test and evaluate Iris consisted of many different parts, from evaluating the algorithms to evaluate the thresholds use for the clients and servers.

# Experiment on Optimal Epidemic Spreading Strategy
The Iris P2P system proposes new ways to deal with the security concerns of threat intelligence sharing. However, many of these ideas need to be verified and explored in simulated experiments in order to understand how a network of peers may behave under different conditions. We simulate and evaluate different spreading strategies in an epidemic sense. As a result of this experiment, we choose the optimal spreading strategy for each different condition and for the protocols for spreading Alerts and for spreading file metadata with different levels of severity.

We decided to run one very large experiment with many parameters instead of a large number of small experiments. In this way it was possible to validate how the conditions relate to each other.

## Goal
The goal of this experiment is to evaluate different spreading strategies based on how fast they spread the message in networks and how much they flood networks with messages. To define a spreading strategy, we need to answer five questions: 

- What algorithm of spreading to use?

  In our case, only the Push algorithm makes sense. The others assume that gossip is constantly updated in the system, and thus peers proactively ask other peers for updates. That is not true in our environment - it might happen that no gossip is spread for a long time. In that case, the proactive update messages in Pull and Push/Pull algorithms are unnecessary.

- To how many nodes should infected nodes spread the message at once?

  We will call this value a spreading factor. Finding the optimal spreading factor is one of the goals of the experiment.

- How long should the infected nodes wait until they ask/spread again?

  We will call this value spreading period. Finding the optimal spreading period is one of the goals of the experiment.

- How do infected nodes choose recipients for spreading from a list of candidates?

  By choosing the recipients completely randomly, we can use the service trust of candidates to design a better heuristic. We propose 3 options:

  - Choose recipients with a uniform probability. Most of the Epidemic Protocols employ this option.
  - Sort recipients based on their service trust and choose first the most trusted ones. This technique assumes that peers with bigger service trust will more likely follow the protocol and thus contribute more to the dissemination of messages.
  - Choose recipients with a probability that exponentially grows with the service trust of each recipient. This technique was already described when we talked about choosing recipients in the Network Opinion Protocol. It works firstly by transforming service trust values of all candidates using an exponential function $f(st) =\frac{a^{st}-1}{a-1}$ with a constant value $a=10$. After that, Iris normalizes the transformed values which represent the probabilities of the candidates being chosen. This technique still favors the trusted peers but also allows one to choose less trusted peers for a bigger variety. The reason is that the previous option (sort by service trust) might result in flooding the trusted peers and not spreading the message to less trusted parts of the network which may also contain benign peers.
- After how much time should the infected node move to a Removed state?

  We will call this value spreading expiration. Optimally, the spreading should stop after the gossip reaches the entire network. Nonetheless, our network is decentralized and does not provide complete information about the status of all peers. For this reason, the spreading expiration should be set beforehand to a duration that guarantees the full convergence. Note that the spreading expiration depends on the previous points because they essentially define the speed of spreading.

As a consequence, we define a _spreading strategy_ as a triplet of:
1. Spreading factor $\in \mathbb{N}$
2. Spreading period $\in \mathbb{N}$
3. Algorithm to choose recipients - we define three options:
  - Choose recipients with uniform probability
  - Choose first the peers with the biggest service trust
  - Choose recipients with a probability that exponentially grows with the service trust of recipients

Finally, after we evaluate the spreading strategies, we should be able to choose an optimal strategy for the following types of messages:

- Alerts: Alert messages should be spread rather quickly to their recipients. The reason is that the event that has caused the alert is usually relevant to the given moment and can help other peers to prepare for an incident.
- File Metadata: Each metadata message has either NORMAL or CRITICAL severity. Each severity level should guarantee different spreading properties. Metadata messages with CRITICAL severity should spread faster to their recipients even for the cost of flooding the network with messages. On the other hand, metadata messages with NORMAL severity do not have to be spread as fast, and thus the peers should choose a spreading strategy that minimizes the magnitude of flooding the network with messages.

# Assumptions
Our experiment makes some important assumptions. First, we make assumptions about the Fides trust model. We assume that, in the long run, the average service trust of all malicious peers is smaller than the average service trust of all benign peers. This assumption essentially means that Fides behaves correctly.

Also, we think it is rational to assume that Fides does not provide peer estimates of service trust values that 100\% match the ground-truth values. We assume that an error of the estimation has a mean $\mu=0$ and a standard deviation $\sigma=0.25$.

Other assumptions are about the network itself. We assume that the churn rate of the network is practically zero. It means we assume that the network is static - no peers join or leave the network. Real networks probably never have a churn rate of zero, but we think that our network will not be too dynamic. The reason is that once a peer joins, it is in his best interest to stay connected for the benefit of collective defense.

Lastly, we assume that the underlying graph of our network is connected. However, the connectivity of the underlying graph is difficult to verify in the real world because we designed our network as an almost unstructured (DHT k-buckets form a small structure) and pure P2P network.

# Methodology
In this section, we describe exactly how we plan to conduct and evaluate the experiment. Firstly, we describe how we generate the networks. Then we elaborate on how exactly our spreading mechanism works. Lastly, we define based on which values we compare the spreading strategies.

Note that we might use the terms graph and network interchangeably.

## Generating Networks
When peers want to send a message to all other peers in the network, the total number of peers in the network is unknown. That is why in our experiment, we generate graphs with the number of nodes uniformly sampled from a range between 2 and 200. We have chosen 200 as an upper bound because we think that is a rational guess for the number of peers in our network in its initial stage of adoption. After that, for every peer, we sample edges representing random outbound connections. We sample a degree for every node's outbound connections from a Poisson distribution with $\lambda=7$. Furthermore, we randomly choose one node that acts as a peer that starts spreading gossip. This algorithm is described in Algorithm 2. Some example networks generated for the experiment with just the described algorithm can be seen in Figure 5.1.

<img width="852" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/f1202487-6822-4e1a-8b54-220610a19e09">


<img width="1124" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/a5fec96d-9ccf-4822-8cc8-c887214a23ce">

After generating a network, we have to select the service trust value for every node. In the experiment, we consider 2 types of peers - malicious and benign. For each graph, we test 4 scenarios which are defined by the ratio of malicious peers in the network. Possible ratios are 0\%, 25\%, 50\% and 75\%. 

However, the behavior of malicious and benign peers is the same. We do not try to model any specific attack scenario. The maliciousness of malicious peers is modeled by on average smaller service trust because we assume that Fides assigned them smaller service trust based on their past malicious behaviour. As stated in assumptions, we assume the average service trust of malicious peers is smaller than the average service trust of benign peers. We distinguish between malicious and benign peers because we would like to see if specific spreading strategies favor only benign or malicious peers. 

In each scenario, we randomly choose the mean $\mu_m$ of service trust of all malicious peers. Then, we sample ground-truth service trusts for all malicious peers from a normal distribution $sr_n = \mathcal{N}(\mu_m,\,0.15)$. The same process is repeated for benign peers. We chose a standard deviation of 0.15 to allow situations where malicious peers have higher service trust than some benign peers because we think it is rational to expect such inaccuracy in our trust model. 

Finally, we choose how every peer views its connected peers in terms of service trust. We realize Fides will most probably estimate the service trust of other peers with some error from ground-truth value. That is why, for every scenario, we randomly choose standard deviation $\sigma_{TM}$ from the set $\{0, 0.05, 0.15, 0.25\}$ that represents the error produced by the underlying trust model. Then, for every edge $(n_1, n_2)$, we sample a service trust view of $n_1$ about $n_2$ from $\mathcal{N}(sr_2,\,\sigma_{TM})$ and vice-versa. This process is described in Algorithm 3.

<img width="730" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/0fca0b97-6b1c-44cf-9c7b-da9a5e20faf2">

## Gossip Spreading
After describing how the networks were generated we only miss the algorithm of how to simulate a spreading strategy in a network.

A spreading period is defined using time. That is why we need to find a way of simulating time. We do that by running our simulation in ticks. One tick represents a time period in which peers can transfer one gossip to peers they share an edge. However, after we find an optimal spreading strategy, we need to convert the ticks back to time by measuring the average duration of one message transfer in the real network.

In the simulation, we treat the ground-truth service trust of every peer as a probability of successfully sending a message to its recipient. For example, if a peer $p$ has a ground-truth service trust of $0.1$, it successfully shares only 1 out of 10 messages despite the fact that any other peer $x$ might view the service trust of $p$ as much higher or lower. 

Every peer keeps a list of candidates for sharing the gossip. In the beginning, the list of candidates for every peer $p_1$ contains peer $p_2$ for every edge $(p_1, p_2)$. Whenever a peer receives the gossip from a sender $s$, it removes $s$ from the list of candidates because peer $s$ already knows about the gossip. Also, whenever the peer successfully shares the gossip with a recipient $r$, it removes recipient $r$ from the list of candidates because the peer $r$ already knows about the gossip.

Peers can only choose recipients of gossip from their list of candidates. If the list is empty, the peer stops spreading the gossip. An algorithm of how to choose recipients from the list of candidates is determined by the currently tested spreading strategy.

In our simulation, we simulate the spreading of only one message in the network. All peers begin in a Susceptible state except the starting peer that starts in an Infected state. Peers move to Infected state after they receive the gossip. From the Infected state, peers can move to the Removed state when their list of candidates is empty. The simulation ends when no peer is in a Susceptible state or the maximum number of allowed ticks has elapsed. 

## Evaluation Technique
We conduct simulations of spreading strategies in two different environments, non-malicious and malicious. In both environments, we want to see which spreading strategies were successful in all networks. We consider a strategy successful in a network if it manages to spread the gossip to all benign peers before the maximum allowed ticks elapse. If no strategy in a given environment succeeds in all networks, we focus on finding strategies that are successful in most networks.

Further, we essentially search for metrics that would show us how fast the most successful strategies manage to spread the gossip and how much they flood the networks with messages. Also, in the malicious environment, we measure these metrics both for the whole network and only for benign peers to see if some strategy produces strictly better results only for benign peers or vice-versa. 

The speed of spreading the message is determined by a tick when all peers have already heard about the message. The intensity of flooding can be calculated by the number of repeated messages in the network. We consider a message repeated if it has been sent to a peer in either an Infected or Removed state (in other words every peer that has already received the gossip before). 

However, the absolute number of repeated messages is not sufficient because it also greatly depends on the end tick of the simulation. Imagine two strategies $s_1$ and $s_2$. The total number of repeated messages both for $s_1$ and $s_2$ is $10$ and $20$, respectively. Strategy $s_1$ seems outperforming $s_2$. However, if strategy $s_1$ ended during the 5th tick, it on average produced 2 repeated messages per tick. If strategy $s_2$ ended during the 100th tick, it produced an average of 0.2 repeated messages. Thus, in the long run, $s_1$ could flood the network significantly more compared to $s_2$. That is why we measure the average number of repeated messages per tick.

Furthermore, we record the ratio of repeated messages to all sent messages in the networks to see if some strategies produce a smaller ratio of repeated messages.

To summarise, for the most successful strategies, we measure:

- Repeated messages per tick: An average number of repeated messages per one tick.
- Ratio of repeated messages: A ratio of repeated messages to all successfully sent messages in the system.
- Average end tick: An average end tick of finished spreading.
- Worst-case end tick: A worst-case end tick of finished spreading. This value should help us decide on a spreading expiration value for the final strategy because it tells us how long it can eventually take until all peers receive the message.

# Results
We present the results of the experiment conducted with the following values. We have generated in total 210 testing spreading strategies as permutations of:
- Spreading factor - $\{1, 2, 3, 5, 7, 9, ALL\}$. ALL stands for all possible recipients in a candidate list.
- Spreading period - $\{1, 2, 3, 5, 10, 20, 50, 100, 250, 500\}$. Each value represents TICKS in a simulation.
- 3 algorithms for choosing recipients

All spreading strategies were simulated in a total of 2,000 different networks which resulted in a total of 420,000 simulations. We have chosen the maximum number of allowed ticks in every simulation of 10,000. 

Note that for clarity, we show results with ticks converted back to time. We have measured that one transfer of a message using Iris takes approximately 300ms. The measurement was conducted between one peer deployed in the CTU network while the other one was deployed in a server in Japan. Because of that, we have decided to convert 1 tick to 500ms to also take into account low-bandwidth and low CPU devices.   

Firstly, we show results of spreading strategies simulating in networks without malicious peers. After that, we show results from the environment with simulated malicious peers. 

## No Malicious Peers in Networks

In this scenario, all peers are considered benign. This still means that some messages can get lost because peers have different ground-truth values of service trust that represent the probability of successfully sending a message. 

Out of a total of 210 strategies, 200 have successfully spread in all the networks before the maximum ticks elapsed. Across all successful strategies, the average ratio of repeated messages is $\mu = 0.74$ with standard deviation $\sigma = 0.028$ and maximum and minimum values $0.68$, $0.78$, respectively. 

As we cannot clearly present results for all the 200 successful strategies, we filter only the most interesting ones. In Table 5.1, we can see the five best and the five worst successful spreading strategies in terms of repeated messages per tick. For these 5 best strategies we can see a total total number of sent messages in Figure 5.2. In contrast, in Table 5.2 we see the 5 best strategies in terms of speed of convergence. The value A in the _choosing recipients field_ in _spreading strategy_ stands for choosing recipients with uniform probability. B represents choosing recipients based on their service trust in descending order. C stands for choosing recipients with a probability that grows exponentially with a view of the recipient's service trust.

<img width="712" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/02976f49-d90e-4fa6-bd22-834920187307">

<img width="701" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/1c066ea0-32a0-46ce-a2eb-0478ccb57aba">

<img width="722" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/a7fd874f-4899-4013-9b3a-087b0e5fdda5">

## Different Ratios of Malicious Peers in Networks
We have simulated spreading strategies in networks with 25\%, 50\%, and 75\% of malicious peers. In all three environments, no spreading strategy successfully spreads the message in all networks. However, in all environments, the most successful spreading strategies were successful in 99\% of all networks. We present the best strategies from these most successful strategies. 

In Table 5.3, we can see an average value of the ratio of repeated messages sent to benign peers along with standard deviation, minimum, and maximum values across the most successful strategies.

<img width="714" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/bf204e1b-13fa-48d0-951d-292784460f2e">

In Table 5.4, we can see for each malicious ratio the best spreading strategies in terms of repeated messages sent to benign peers per tick. For these strategies, Figure 5.3 shows the total number of messages sent to benign peers. In Table 5.5, we can see for each malicious ratio the best spreading strategies in terms of average end tick of spread to benign peers. The value A in _choosing recipients_ field in _spreading strategy_ stands for choosing recipients with uniform probability. B represents choosing recipients based on their service trust in descending order. C stands for choosing recipients with a probability that grows exponentially with a view of the recipient's service trust.

<img width="718" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/1ced60cc-cf3b-41f3-89eb-bebaa7438b2e">

<img width="720" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/65a0ac1a-9205-45a9-b392-5bd673a8f793">

<img width="728" alt="image" src="https://github.com/stratosphereips/iris/assets/2458867/0fbc3abd-76fa-4c13-911e-acc90cb3891d">

# Discussion
Regardless of the number of malicious peers in the networks, spreading strategies with the fastest convergence of spreading are the ones with the biggest possible spreading factor and the smallest possible spreading period. Such results are logical because in these strategies peers simply send the message to all possible candidates as soon as possible. On the other hand, the strategies that produce the smallest number of repeated messages per tick are the slowest strategies - the ones with the smallest spreading factor and the biggest \spreading period. This also makes sense because a larger spreading period makes the simulation take more ticks and that is why the value of repeated messages per tick decreases.   

A significant discovery of this experiment is that we can decrease the ratio of repeated messages sent in the overall system and more importantly sent to benign peers by spreading the message slowly. We see that one of the best strategies in terms of repeated messages per tick in the non-malicious environment produced a ratio of repeated messages $0.68$. On the other hand, the best strategy in terms of speed of convergence produced a ratio of repeated messages $0.78$. We observe a 10\% difference. This fact holds strongly even in environments with malicious peers. By comparing the same values, we see that in the environment with 25\% of malicious peers, we can reduce the ratio of repeated messages sent to benign peers from $0.76$ to $0.66$ by spreading slowly. In the environment with 50\% malicious peers, we can reduce the ratio of repeated messages sent to benign peers from $0.74$ to $0.63$ and in the environment with 75\% malicious peers from $0.72$ to $0.60$. The improvement is always at least 10\%. This means that no matter the number of malicious peers in the system, we can decrease the total number of repeated messages sent to benign peers by at least 10\% by spreading the message slowly. The reason is that by spreading the message slowly, we can avoid situations when peers send messages to each other simultaneously without the knowledge that the other peer already knows about the message. 

If we look at the best spreading strategies in terms of repeated messages per tick sent to benign peers, we see that the top 3 strategies differ only in the algorithm for choosing recipients (except for the environment with 75\% of malicious peers) - strategies (1, 100, -). It means that in all environments except the one with 75\% of malicious peers, the algorithms for choosing recipients have no substantial effect in moderating the level of flooding. The change occurs in the environment with 75\% malicious peers where the best strategies in terms of repeated messages per tick sent to benign peers choose recipients with a probability that exponentially grows with candidates' service trust. It means that if we assume a highly adversarial network, we can actually benefit from using service trust as a heuristic to choose message recipients. 

Moreover, service trust value has no effect if we want to share the message as fast as possible because all the fastest strategies simply try to send the message to all available peers in the list of candidates. That is why the algorithm for choosing recipients is actually redundant.

In Table 5.3, we can see the distribution of the ratio of repeated messages sent to benign peers across all strategies in malicious environments. We can see that the mean values decrease disproportionately with the ratio of malicious peers in the network. A wrong interpretation would be to say that the more malicious peers, the better. That is not correct. In Table 5.5, we can see that the worst-case duration of spreading grows proportionally with the maliciousness of the network. The reason is that the networks become so untrustworthy that almost no message is successfully sent. 

As we already stated, the fastest spreading strategies are the ones that send the message to all possible peers as fast as possible, and the algorithm that chooses recipients is redundant. However, to decide the best strategies while optimizing the repeated messages per tick, we have plotted the best strategies from Tables 5.1 and 5.4 in Figures 5.2 and 5.3. The figures show the total number of messages sent to benign peers over time - that is why the lower the _y_ axis, the better. From the Figures, we conclude that strategy (1, 100, A) has the best performance in environments from 0\% to 50\% of malicious peers. In an environment with 75\% of malicious peers, strategy (1, 50, C) has the best performance. If we use the conversion again that 1 tick equals 500ms, we get the best strategy (1, 50, A) for non-to-medium malicious networks and (1, 25, C) for highly adversarial networks. Let us remember that algorithm A stands for choosing recipients with uniform probability, while C represents choosing recipients with a probability that exponentially grows with candidates' service trust.

Another outcome of the experiment is that we can estimate how long it can eventually take to spread the message to all benign peers using certain strategies in a given environment. For the estimation, we can utilize the worst-case duration column in the result Tables. For example, in Tables 5.2 and 5.5 we can see that the fastest spreading strategies may take from 10s in non-malicious environments up to 40s in the most malicious environment. On the other hand, if we focus on optimizing the number of sent repeated messages to benign peers per tick by spreading slowly, we can see in Tables 5.1 and 5.4 that the best strategies may take from 45 minutes in a non-malicious environment up to 80 minutes in the most malicious environment.  

It is also important to discuss if the simulated networks behave the same way as the real networks would behave. We have assumed that the simulated networks are static - edges in the under-laying graph do not change. In reality, peer-to-peer networks can never guarantee such property. On the other hand, in dynamic networks, the number of nodes and edges may change. To design the best spreading strategies in such an environment, we would have to be able to measure the up-time of peers to choose recipients that have a bigger probability of not leaving the network after we share the gossip with them.

Another important note is that in the experiment, we have not considered a malicious actor that would try to exploit the epidemic protocol by disseminating a large number of messages. Such action could result in flooding the network with a substantial number of messages and potentially leading to a DoS of the entire network. A possible mitigation for such an attack is to employ some form of rate-limiting per individual peers. Every peer would keep track of the number of sent messages by all its neighbors (or the number of bytes) and allow only a certain amount of them for each neighbor per time unit. 

Lastly, we could have designed values that define spreading strategies differently. For example, the spreading factor and spreading period could be defined as ranges from which every peer randomly chooses values that define its spreading strategy. However, the number of possible combinations is large and that is why we have not chosen this approach in our experiment. Another different option on how to choose the value of the spreading factor is, for example, by setting the spreading factor of every peer to a specific percentage of all its connections. 


















































  

