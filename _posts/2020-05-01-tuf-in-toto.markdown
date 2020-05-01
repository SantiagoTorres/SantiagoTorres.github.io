---
layout: post
title:  "How to easily try out TUF + in-toto"
date:   2020-05-01 17:00:00 -0400
categories: CI Security
---

I've been speaking quite a lot with quite a lot of people about the benfits of
in-toto and TUF together. Indeed, my reaction after saying "hey, you don't
*need* TUF to use in-toto", is "but they do go really well together".
I've done it so much that by now I have a very well rehearsed canned answer as
to why they go well. It was only a matter of will and free time (look ma! I'm a
Doctor now!), before I decided to dust off this blog and probably share why it
matters and --- more importantly --- how you can see it for yourself in four
easy steps.

## What is TUF and in-toto and how they are different?

So, as I said, I generally start my engagements with people asserting TUF !=
in-toto, and the reason why is because they are generally conflated together
because they come from similar teams and follow similar design principles.
However, they serve the same overarching goal: *secure delivery of content* but
they provide different *security properties*.  So, to make things super clear,
they are not the same --- they complement each other.

### What is TUF? TUF stores sTUFf (and does other stuff as well)

TUF started as an Update Framework, but as noted by a lot of people, it is
actually a very neat way to provide trust information about arbitrary
collections of software elements (anything you can hash, really). We oftentime
refer to these as *software artifacts*. However, TUF can *also* provide trust
information about other metainformation about these artifacts. Think of TUF as
some sort of very powerful mechanism to store sTUFf securely.

Not only TUF stores sTUFf, but it also allows you to make sure these artifacts
actually came from whoever should've put them there. Say, that you trust your
friend Eliza who owns a pharmacy to give you a bottle of pills. With TUF (and
if we were able to hash bottles of pills), you could make sure that this bottle
of pills was put in the counter (i.e., a repository) by Eliza and Eliza only.
So, in other words, TUF ensures *authenticity of the provider of the data it's
storing*.

If we were talking in person I would've eluded to my fantastic car salesman
voice, but given that you're reading it you'll have to do the heavy lifting,
because there's more! 

TUF also ensures other very important things, like the software artifacts being
fresh. That is, that your bottle of pills from the previous example is not
actually an old one.

Lastly, and very importantly, it also ensures that the repository where all
these software artifacts are located follows a consistent state. This is
important, because as it has been noted before, attackers can _mix and match_
software artifacts in such a way that the sum of their parts is actually
malicious. This would be akin to having somebody using different versions of
Eliza's pharmaceutical offerings and tricking you into taking two very
incompatible chemicals[^1]  --- technically, you git it all from Eliza didn't
you?

So to wrap this up. Imagine TUF being this system that ensures that you:

- Got what you wanted
- From who's supposed to put it there
- That it's not expired or old
- And that there is a consistent state of the place you got them to avoid many
  things

(Now, TUF does other neat things, but these are the big selling points in my
opinion)

Great, so I've told you about TUF, let me go ahead and introduce its sister:
in-toto.

### in-toto answers how Eliza got her sTUFf

Now, a crucial question that you may ask about Eliza's pharmacy is: "well I
trust Eliza, and she hopefully is selilng me things that were FDA approved and
whatnot". And the truth is, unfortunately, you don't know. In the world of
software as the stakes are, you either walk back yourself or hope that people
aren't lying about what they put in their software repositories. In other
words, in-toto allows you to do cool things like put FDA approval stamps on
Eliza's pills.

To do this, in-toto creates a cryptographic paper trail that's very akin to
Bills of Materials (in fact, in-toto is very related to cryptographically
enforce-able bills of materials), so that you can walk a
**cryptographically-authenticated paper trail** from your bottle of pills (err,
software artifact), all the way to the raw materials that created it (e.g.,
think of source code, configuration files, etc)

This way, you have a very strong coallition of products, one that ensures
everything is very tighly sealed and packaged (TUF), and one that gives you
cryptographic visibility on the process that produced what you just got
(in-toto).

## TUF and in-toto together

The basic idea is simple, we will use in-toto in the pipeline to create the
paper trail, and then we will use TUF to store all the sTUFf. We will do this
in basically four steps, and here they are:

1. Initialize a TUF repository 
2. Create an in-toto layout and register it in a special place in the TUF
   repository
3. Carry out your pipeline as you normally would, but create in-toto
   attestations that are submitted to a TUF repository
4. Profit

I took the liberty of gathering a bunch of demos that both the in-toto and TUF
communities put together through countless hours and stitched them together to
create this four-step process to profit.  You can get it from
[here](https://github.com/SantiagoTorres/tuf_in_toto_demo), you'll see it has a
bunch of submodules so make sure you're cloning recursively (with the -r flag)

So let's go and do it!

### 0. Set up your environment

Ok, I lied. it's five steps. The first one is to install TUF and in-toto. You
can probably use a virtualenv and install them from pip:

    $ pip install tuf in-toto pynacl cryptography

Done. I also threw in the pynacl dependencies and cryptography so you can use
any keys you like --- this deal won't last forever!

### 1. Initialize the tuf repository

So, you can grok the script under scripts/init.py, or you can blindly execute
my code (tough choice, I know). Either way, once you run it or read it you'll
find out it basically does the following:

1. Sets up a place to store your repository metadata (think of it as git
   init-ing things)
2. Goes ahead and sets up the trust relationships (i.e., it says, I trust this
   key for packages, this one for layouts and links).
3. Sets up your client environment (i.e., copies the root of trust into the
   client directory)

Yes, with 50 lines of code and you have your own shiny TUF/in-toto repo. Order
today!

### 2. Creating and publishing a layout

I tried to reduce code duplication around, so I copied the layout from the
basic [in-toto demo](https://github.com/in-toto/demo), which basically starts
from a git repository and then finally creates a tarball called
"demo-package.tar.gz". This is our bottle of pills.

However, before we make all this, we want to create an in-toto layout, which is
a policy file which will describe how our supply chain should actually look
like. This time, run the script to publish this:

    $ python scripts/publish.py

This will do the following:

1. Create this layout and sign it with the root of trust
2. Add it to a special location in the TUF repository

Done, a couple of lines more and now you have a TUF repository publishing
in-toto layouts. We will use these layouts later when we want to make sure our
pipeline was followed to the letter.

Now that you have something published, it may be a good time to serve the
content using the accompanying script:
    
    $ bash create_server.sh 

In another terminal so you can see your TUF repo in action.

### 3. Carry our the pipeline 

Now, we do our usual stuff, code some, pre-commit some stuff, package it and
put it somewhere so people can download it. So let's do just that, but use
in-toto tooling to create cryptographic attestations of what happened so we can
create an audit trail. This was shamelessly copied as well from the in-toto
demo modulo a small wrapper to *also* put these attestations in our TUF
repository. You can run:

    $ python scripts/run.py

And see it all happen with your own eyes.

### 4. Now verify it's all together

At last, it's time to consume our package. To do this, we will download things,
then make sure they are kosher and finally open it to unwrap what's inside.
This is very similar to how things in the meatspace work. Let's think about our
bottle of pills again:

1. You your new bottle of pills from your medicine cabinet
2. You ensure that the tamperproof seal around it is nice, and that the
   expiration dates are correct (TUF)
3. If you want to be extra sure, you will also make sure there's an FDA
   approval seal and notice a lot-number besides the expiration date (in-toto)

Once you notice all these things, then you go ahead and open the bottle. 

Software shouldn't be too different. In fact, this is what our downloader will
do. In something shy of 30 lines, it will first use TUF to connect to our
repository and download our package, then it will notice there is also other
information that's attached to it and download it too. Once it's all downloaded 
it will go ahead and run in-toto verification on it. If everything is ok, then
you will happily consume your new package:

    $ tar xvf demo-package.tar.gz && pyton demo-package/foo.py

That's it!

## Where do we go from here?

There are a lot of resources to work with in-toto and TUF. I usually put things into two buckets. You can do things *with* TUF and in-toto or you could do things *for* TUF and in-toto. 

For the first, you can set up a repository and play with things more by
tweaking these scripts. You can also take a look at the documentation and
explore ways to add these tools to your environments and ecosystems. Shoot an
email to the [TUF](theupdateframework@googlegroups.com) or
[in-toto](in-toto-public@googlegroups.com) lists if you ever run into issues as
we'd be more than hapy to help

If you are interested in also developing *for* in-toto or TUF, these
communities are super, super welcoming, and I'd encourage you to reach out and
play with things.  There are already some labels for newcomers in the issues. I
think there are places to work in which we could use more hands:

1. We have a [golang library](https://github.com/in-toto/in-toto-golang) that
   needs more love: it's a somewhat feature-complete implementation but it
   could use more work on the non core in-toto features. If you like go, I
   think this is a great place to leave a mark.
2. The [Jenkins Plugin](https://github.com/jenkinsci/in-toto-plugin) and the
   [Kubernetes Admission controller](https://github.com/in-toto/in-toto-webhook)
   are also great places to work with things. I'd suggest you take a
   look at the repositories and play with them a little bit. 
3. Anything you'd like really. If you have ideas on how to make things better
   I'm sure that we'd be more than happy to hear them.

I hope this all helps, and see you around!

## Acknowledgements

So, this is nothing new, and actually you can read how Datadog does this very
well
[here](https://www.datadoghq.com/blog/engineering/secure-publication-of-datadog-agent-integrations-with-tuf-and-in-toto/).
This blogpost and demo is of course inspired on the work by Trishank Kuppusamy,
who made it all happen on the Datadog side of things. You may also want to read how this is getting encoded into an in-toto ITE [here](https://github.com/in-toto/ITE/pulls/4)



[^1]: I'm not a chemist and I'm not going to give you any bad ideas so the example chemicals are left as an exercise to the reader.
