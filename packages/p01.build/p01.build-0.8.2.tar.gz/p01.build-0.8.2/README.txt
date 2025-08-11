This package provides a product build, release and deploy system based on
package versions using zc.buildout. The core concept is taken from keas.build
and provides the same configuration syntax. The main difference is that we
don't setup the install script as ``install`` because there is a conflict with
the gnu install script call on ubuntu (pycairo, python waf install) used by a
popen recipe (p01.recipe.setup:popen). This implementation will offer the
install script as a ``deploy`` entry_point. The deploy entry point called deploy
was removed and is not supported. Use salt or another concept for calling the
deploy method your your server.
